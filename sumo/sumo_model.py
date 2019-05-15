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
        self._patient_values = { key: { k: [] for k in self.field_labels } for key in self._cohort_list }
        self._load_patients()
        if self._patients:
            self._calc_stats()
            self.save()

        return self.stats

    @property
    def stats_by_field(self):
        if not self.stats:
            return []

        field_dict = { k: { "cohorts": {}, "matched_pairs": {}, "comparison": {} } for k in self.field_labels }   

        for cohort, cohort_fields in self.stats["cohorts"].items():
            for field_name, field_stats in cohort_fields.items():
                field_dict[field_name]['cohorts'][cohort] = field_stats

        for cohort_pair, field_stats in self.stats["matched_pairs"].items():
            for field_name, fstats in field_stats.items():
                field_dict[field_name]['matched_pairs'][cohort_pair] = fstats 

        for cohort_pair, field_stats in self.stats["comparison"].items():
            for field_name, fstats in field_stats.items():
                field_dict[field_name]['comparison'][cohort_pair] = fstats

        stats = { "fields": field_dict, "distribution": self.stats['distribution'] }    

        return stats


    def compare_cohorts(self, cohort1, cohort2):
        if not self.stats:
            raise Exception("stats not defined")

        summary = { k: {} for k in self.field_labels }
        for item in self.field_labels:        
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
        summary = { k: [] for k in self.field_labels }
        cohort1_patients = [ p for p in self._patients if p.cohort == cohort1 ]
        cohort2_patients = [ p for p in self._patients if p.cohort == cohort2 ]
        matched_pairs = []
        for patient in cohort1_patients:
            match = [ p for p in cohort2_patients if p.pair_id == patient.pair_id ]
            if match:
                matched_pairs.append((patient, match[0]))

        for pat1, pat2 in matched_pairs:
            for item in self._field_list:
                value1 = pat1.fieldValue(item)
                value2 = pat2.fieldValue(item)
                if value1 is not None and value2 is not None:
                    try:
                        diff = value1 - value2
                    except:
                        continue
                    else:
                        field_label = self.field_label(item)
                        summary[field_label].append(diff)

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
    

    def field_label(self, field):
        field_parts = [x.strip() for x in field.split(' ')]
        len_field_parts = len(field_parts)
        if len_field_parts in (0,1,3):
            return field
        else:
            return field_parts[-1]

    @property
    def field_labels(self):
        return [self.field_label(f) for f in self.foa.split(',')]


    
    def _calc_stats(self):
        self.stats = { "distribution": { k: {} for k in self.field_labels}, "comparison": {}, "matched_pairs": {},
                    "cohorts" : { key: { k: { "mean": None, "std": None, "median": None, "iqr": None, 
                    "ratio": None, "n": 0, 'exposures': 0 } for k in self.field_labels } for key in self._cohort_list }}
        no_patients = len(self._patients)
        field_list = [x.strip() for x in self.foa.split(',')]
        
        distribution = { k: { c: {} for c in self._cohort_list } for k in self.field_labels}
        for field_key in distribution.keys():
            distribution[field_key]['total'] = {}

        for field in field_list:
            field_label = self.field_label(field)
            is_numeric = True
            for patient in self._patients:
                value = patient.fieldValue(field)
                if type(value) in (str, unicode): # auto categorize + set exposure
                    is_numeric = False
                    self.stats['cohorts'][patient.cohort][field_label]['n'] += 1
                    if self.exposure_level and value and value.lower() == self.exposure_level.lower():
                        self.stats['cohorts'][patient.cohort][field_label]['exposures'] += 1
                    distribution[field_label]['total'].setdefault(value, 0)
                    distribution[field_label]['total'][value] += 1
                    distribution[field_label][patient.cohort].setdefault(value, 0)
                    distribution[field_label][patient.cohort][value] += 1

                elif type(value) in (int, float): #value is numeric
                    self._patient_values[patient.cohort][field_label].append(value)
                    if value:
                        if self.exposure_level:
                            try:
                                if value >= float(self.exposure_level):
                                    self.stats['cohorts'][patient.cohort][field_label]['exposures'] += 1
                            except:
                                pass
                        else:
                            self.stats['cohorts'][patient.cohort][field_label]['exposures'] += 1

                    if self.category_list:
                        category = utils.categorize_by_list(self.category_list, value)
                        distribution[field_label]['total'].setdefault(category, 0)
                        distribution[field_label]['total'][category] += 1
                        distribution[field_label][patient.cohort].setdefault(category, 0)
                        distribution[field_label][patient.cohort][category] += 1
                else:
                    continue # value is probably None
            
            # field distributions
            if is_numeric:   #numeric values, sort categories
                for cohort, val_counts_dict in distribution[field_label].items():
                    self.stats["distribution"][field_label][cohort] = [(k, v) for k, v in val_counts_dict.items()]
                    self.stats["distribution"][field_label][cohort].sort(key=lambda x: list(map(lambda y: (float(y[1]),y[0]), [x[0].split(' ')]))[0])

            elif self.category_list: #ordinal/ordered
                for cohort, val_counts_dict in distribution[field_label].items():
                    distribution = []
                    for ordinal in self.category_list:
                        ordinal_val = val_counts_dict.get(ordinal)
                        if ordinal_val:
                            distribution.append((ordinal, ordinal_val))
                    self.stats["distribution"][field_label][cohort] = distribution

            else: # no particular order, nominal
                for cohort, val_counts_dict in distribution[field_label].items():
                    self.stats["distribution"][field_label][cohort] = [(k, v) for k, v in val_counts_dict.items()]

        cohort_list = self._cohort_list

        for field in field_list:
            field_label = self.field_label(field)
            for cohort in cohort_list:
                values = self._patient_values[cohort][field_label]

                if values:
                    self.stats['cohorts'][cohort][field_label]['mean'] = np.mean(values)
                    self.stats['cohorts'][cohort][field_label]['std'] = np.std(values)
                    self.stats['cohorts'][cohort][field_label]['iqr'] = np.subtract(*np.percentile(values, [75, 25]))
                    self.stats['cohorts'][cohort][field_label]['median'] = np.median(values)  
                    self.stats['cohorts'][cohort][field_label]['n'] = len(values)

                n = self.stats['cohorts'][cohort][field_label]['n']
                if n:
                    exposures = self.stats['cohorts'][cohort][field_label]['exposures']
                    self.stats['cohorts'][cohort][field_label]['ratio'] = exposures / float(n)
        
        
        if cohort_list and len(cohort_list) > 1:
            for i, cohort1 in enumerate(cohort_list):
                if i + 1 == len(cohort_list):
                    break
                cohort_sub_list = cohort_list[i+1:]
                for cohort2 in cohort_sub_list:
                    self.stats["comparison"][cohort1 + " - " + cohort2] = self.compare_cohorts(cohort1, cohort2)
                    self.stats["matched_pairs"][cohort1 + "/" + cohort2] = self.compare_cohort_matched_pairs(cohort1, cohort2)


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
        field_list = self._field_list
        for field in field_list:
            for table, fieldname in utils.getfieldparts(field):
                table_fields = kw.setdefault(table,[])
                if fieldname not in table_fields:
                    table_fields.append(fieldname)
        return kw

    @property
    def _field_list(self):
        return [x.strip() for x in self.foa.split(',')]


   