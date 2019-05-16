from orm import Patient, omop
from sumo.sumo_model import Sumo


project_id = 'test_rondo_integration'

if __name__ == '__main__':
    #simple cohort example with numeric field of analysis
    sumo1 = Sumo.upsert(project_id=project_id, name="Example: Simple numeric", defaults=dict(cohorts='A,B,C,D', foa='Person.year_of_birth yob'))
    sumo1.save()
    sumo1.analyse()

    #simple cohort example with categorical field of analysis
    sumo2 = Sumo.upsert(project_id=project_id, name="Example - numeric exposure level", defaults=dict(cohorts='A,B', exposure_level='1970', foa='Person.year_of_birth'))
    sumo2.save()
    sumo2.analyse()

    #simple cohort example with ordinal field of analysis
    sumo3 = Sumo.upsert(project_id=project_id, name="Example: numeric distribution", defaults=dict(cohorts='A,B,D', distribution_levels='1960, 1962, 1965, 1970', foa='Person.year_of_birth'))
    sumo3.save()
    sumo3.analyse()

    #example of numerical with exposure level
    sumo4 = Sumo.upsert(project_id=project_id, name="Example: simple nominal", defaults=dict(cohorts='A,B', exposure_level='french', foa='Person.ethnicity_source_value'))
    sumo4.save()
    sumo4.analyse()


    #example of nominal with exposure level
    sumo5 = Sumo.upsert(project_id=project_id, name="Simple ordinal", defaults=dict(cohorts='A,B', distribution_levels='french, irish', foa='Person.ethnicity_source_value'))
    sumo5.save()
    sumo5.analyse()

    #example of numerical field with distribution
    sumo6 = Sumo.upsert(project_id=project_id, name="Simple date", defaults=dict(cohorts='A,B,C', foa='Condition_occurrence.condition_start_date'))
    sumo4.save()
    sumo4.analyse()











    

