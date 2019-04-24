import uuid
from random import randint

from orm.model import Model
from orm.patient import Patient
from orm import omop
import numpy as np
from . import utils


class Sumo(Model):
    _name = "sumo"

    def analyse(self):
        self._patient_values = { key: { k: [] for k in self._field_list } for key in self._cohort_list }
        self._load_patients()
        if self._patients:
            self._calc_stats()
            self.save()

        return self.stats

    @property
    def stats_by_field(self):
        #import pdb
        #pdb.set_trace()
        if not self.stats:
            return []

        field_dict = { k: { "cohorts": {}, "matched_pairs": {}, "comparison": {} } for k in self._field_list }   

        for cohort, cohort_fields in self.stats["cohorts"].items():
            for field_name, field_stats in cohort_fields.items():
                field_dict[field_name]['cohorts'][cohort] = field_stats

        for field_name, field_stats in self.stats["matched_pairs"].items():
            field_dict[field_name]['matched_pairs'] = field_stats   

        for field_name, field_stats in self.stats["comparison"].items():
            field_dict[field_name]['comparison'] = field_stats 

        stats = { "fields": field_dict, "categorized": self.stats['categorized'] }    

        return stats


    def compare_cohorts(self, cohort1, cohort2):
        if not self.stats:
            raise Exception("stats not defined")

        summary = { k: {} for k in self._field_list }
        for item in self._field_list:        
            try:
                summary[item]['OR'] = self.stats['cohorts'][cohort1][item]['ratio'] / self.stats['cohorts'][cohort2][item]['ratio']
            except:
                summary[item]['OR'] = None

            try:
                summary[item]['mean'] = self.stats['cohorts'][cohort1][item]['mean'] - self.stats['cohorts'][cohort2][item]['mean']
                summary[item]['median'] = self.stats['cohorts'][cohort1][item]['median'] - self.stats['cohorts'][cohort2][item]['median']
                summary[item]['std'] = self.stats['cohorts'][cohort1][item]['std'] - self.stats['cohorts'][cohort2][item]['std']
                summary[item]['iqr'] = self.stats['cohorts'][cohort1][item]['iqr'] - self.stats['cohorts'][cohort2][item]['iqr']
            except: #probably a nominal field
                pass
        return summary


    def compare_cohort_matched_pairs(self, cohort1, cohort2):
        summary = { k: [] for k in self._field_list }
        cohort1_patients = [ p for p in self._patients if p.cohort == cohort1 ]
        cohort2_patients = [ p for p in self._patients if p.cohort == cohort2 ]
        matched_pairs = []
        for patient in cohort1_patients:
            match = [ p for p in cohort2_patients if p.pair_id == patient.pair_id ]
            if match:
                matched_pairs.append((patient, match[0]))

        for pat1, pat2 in matched_pairs:
            for item in self._field_list:
                table, field = item.split('__')
                try:
                    value1 = getattr(pat1, "_%s" % (table)).get(field)
                    value2 = getattr(pat2, "_%s" % (table)).get(field)
                except:
                    pass
                try:
                    diff = value1 - value2
                except: #probably a nominal field
                    continue
                else:
                    summary[item].append(diff)

        stats = {}
        for field, diffs in summary.items():
            if diffs:
                stats[field] = {}
                stats[field]['mean'] = np.mean(diffs)
                stats[field]['median'] = np.median(diffs)
                stats[field]['std'] = np.std(diffs)
                stats[field]['n'] = len(diffs)
                stats[field]['iqr'] = np.subtract(*np.percentile(diffs, [75, 25]))

        return stats


    @property
    def category_list(self):
        cats = utils._split_string(self.categories)
        try:
            cats.sort()
        except:
            return None
        else:
            return cats


    def _calc_stats(self):
        
        self.stats = { "categorized": { k: None for k in self._field_list }, 
                    "cohorts" : { key: { k: { "mean": None, "std": None, "median": None, "iqr": None, 
                    "ratio": None, "n": 0, 'exposures': 0 } for k in self._field_list } for key in self._cohort_list }}
        no_patients = len(self._patients)

        for field in self._field_list:
            categorized = {}
            table, fieldname = field.split('__')
            for patient in self._patients:
                try:
                    value = float(getattr(patient, "_%s" % (table)).get(fieldname))
                    
                except: 
                    try: #value is a string 
                        value = getattr(patient, "_%s" % (table)).get(fieldname) 
                    except: #value is probably non-exisitent
                        value = None
                    else: # auto categorize + set exposure
                        self.stats['cohorts'][patient.cohort][field]['n'] += 1
                        if value == self.exposure_level:
                            self.stats['cohorts'][patient.cohort][field]['exposures'] += 1
                        cat_counts = categorized.setdefault(value, 0)
                        categorized[value] = cat_counts + 1

                else: #value is numeric
                    self._patient_values[patient.cohort][field].append(value)
                    if value:
                        if self.exposure_level:
                            try:
                                if value >= float(self.exposure_level):
                                    self.stats['cohorts'][patient.cohort][field]['exposures'] += 1
                            except:
                                pass

                        else:
                            self.stats['cohorts'][patient.cohort][field]['exposures'] += 1

                    if self.category_list:
                        category = utils.categorize_by_list(self.category_list, value)
                        cat_counts = categorized.setdefault(category, 0)
                        categorized[category] += 1

            self.stats["categorized"][field] = [(k, v) for k, v in categorized.items()]
            if self._patient_values[patient.cohort][field]:   #numeric values, sort categories
                self.stats["categorized"][field].sort(key=lambda x: list(map(lambda y: (float(y[1]),y[0]), [x[0].split(' ')]))[0])


        for field in self._field_list:
            for patient in self._patients:
                values = self._patient_values[patient.cohort][field]

                if values:
                    self.stats['cohorts'][patient.cohort][field]['mean'] = np.mean(values)
                    self.stats['cohorts'][patient.cohort][field]['std'] = np.std(values)
                    self.stats['cohorts'][patient.cohort][field]['iqr'] = np.subtract(*np.percentile(values, [75, 25]))
                    self.stats['cohorts'][patient.cohort][field]['median'] = np.median(values)  
                    self.stats['cohorts'][patient.cohort][field]['n'] = len(values)

                n = self.stats['cohorts'][patient.cohort][field]['n']
                if n:
                    exposures = self.stats['cohorts'][patient.cohort][field]['exposures']
                    self.stats['cohorts'][patient.cohort][field]['ratio'] = exposures / n

        cohort_list = self._cohort_list
        if cohort_list and len(cohort_list) > 1:
            self.stats["comparison"] = self.compare_cohorts(cohort_list[0], cohort_list[1])
            self.stats["matched_pairs"] = self.compare_cohort_matched_pairs(cohort_list[0], cohort_list[1])

            


    @property
    def _cohort_list(self):
        return utils._split_string(self.cohorts)


    def _load_patients(self, limit=None):
        _field_dict = self._field_dict
        if type(self._patients) is list:
            return self._patients
        else:
            patients = Patient.filter(project_id=self._project_id, 
                cohort=self._cohort_list, omop=list(_field_dict.keys()))

            cohort_counts = {}
            pats = []
            for patient in patients:
                #patient.pair_id = None
                if limit:
                    cohort_count = cohort_counts.setdefault(patient.cohort, 0)
                    if cohort_count < limit:
                        cohort_counts[patient.cohort] = cohort_count + 1
                        pats.append(patient)
                else:
                    pats.append(patient)
                #patient._field_updates.clear()

            self._patients = pats

    @property
    def _field_dict(self):
        kw = {}
        if not self.foa:
            return kw

        keywords = utils._split_string(self.foa.replace('.','__'))
        for keyword in keywords:
            try:
                table, field = keyword.split('__')
            except:
                pass
            else:
                table = utils.sanitize_key(table)
                field = utils.sanitize_key(field)
                table_fields = kw.setdefault(table.capitalize(),[])
                if field.lower() not in table_fields:
                    table_fields.append(field.lower())
        return kw

    @property
    def _field_list(self):
        l = []
        for k, vl in self._field_dict.items():
            for v in vl:
                l.append("%s__%s" % (k,v))
        return l


   