import uuid
from random import randint

from orm.model import Model
from orm.patient import Patient
from orm import omop
import numpy as np


class Sumo(Model):
    _name = "rondo"

    def analyse(self):
        self.stats = { "cohorts" : { key: { k: { "mean": None, "std": None, "irq": None } 
                        for k in self._field_list } for key in self._cohort_list }}
        self._patient_values = { key: { k: [] for k in self._field_list } for key in self._cohort_list }
        self._load_patients()
        self._calc_stats()
        if self.cohort_pairs and len(self.cohort_pairs) == 2:
            self.stats["comparison"] = self.compare_cohort_matched_pairs(*self.cohort_pairs)
            self.stats["matched_pairs"] = self.compare_cohort_matched_pairs(*self.cohort_pairs)

        return self.stats


    def compare_cohorts(self, cohort1, cohort2):
        if not self.stats:
            raise Exception("stats not defined")

        summary = { k: {} for k in self._field_list }
        for item in self._field_list:
            table, field = item.split('.')
            summary[item]['mean'] = self.stats['cohorts'][cohort1][item]['mean'] - self.stats['cohorts'][cohort2][item]['mean']
            summary[item]['or'] = self.stats['cohorts'][cohort1][item]['mean'] - self.stats['cohorts'][cohort2][item]['mean']
            summary[item]['median'] = self.stats['cohorts'][cohort1][item]['median'] - self.stats['cohorts'][cohort2][item]['median']
            summary[item]['std'] = self.stats['cohorts'][cohort1][item]['std'] - self.stats['cohorts'][cohort2][item]['std']
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
                table, field = item.split('.')
                value1 = getattr(pat1, "_%s" % (table)).get(field)
                value2 = getattr(pat2, "_%s" % (table)).get(field)
                diff = value1 - value2
                summary[item].append(diff)

        stats = {}
        for field, diffs in summary.items():
            stats[field] = {}
            stats[field]['mean'] = np.mean(diffs)
            stats[field]['median'] = np.median(diffs)
            stats[field]['std'] = np.std(diffs)

        return stats


    def _calc_stats(self):
        no_patients = len(self._patients)
        for table, fields in self._field_dict.items():
            for field in fields:
                for patient in self._patients:
                    try:
                        value = getattr(patient, "_%s" % (table)).get(field)
                        
                    except TypeError:
                        pass
                    else:
                        if value:
                            self._patient_values[patient.cohort]["%s.%s" % (table, field)].append(value)

        for table, fields in self._field_dict.items():
            for field in fields:
                for patient in self._patients:
                    values = self._patient_values[patient.cohort]["%s.%s" % (table, field)]
                    if values:
                        self.stats['cohorts'][patient.cohort]["%s.%s" % (table, field)]['mean'] = np.mean(values)
                        self.stats['cohorts'][patient.cohort]["%s.%s" % (table, field)]['std'] = np.std(values)
                        self.stats['cohorts'][patient.cohort]["%s.%s" % (table, field)]['iqr'] = np.subtract(*np.percentile(values, [75, 25]))
                        self.stats['cohorts'][patient.cohort]["%s.%s" % (table, field)]['median'] = np.median(values)


    @property
    def _cohort_list(self):
        split_on = ','
        if split_on not in self.cohorts:
            split_on = ' '
        keywords = [x.strip() for x in self.cohorts.split(split_on)]
        cohort_list = list(dict.fromkeys(keywords))
        return cohort_list


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

        split_on = ','
        if split_on not in self.foa:
            split_on = ' '
            
        keywords = [x.strip() for x in self.foa.split(split_on)]

        keywords = list(dict.fromkeys(keywords))
        for keyword in keywords:
            try:
                table, field = keyword.split('.')
            except:
                pass
            else:
                table_fields = kw.setdefault(table.capitalize(),[])
                if field.lower() not in table_fields:
                    table_fields.append(field.lower())
        return kw

    @property
    def _field_list(self):
        l = []
        for k, vl in self._field_dict.items():
            for v in vl:
                l.append("%s.%s" % (k,v))
        return l


   