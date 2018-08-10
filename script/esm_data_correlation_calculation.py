import csv, sys
from scipy import stats

interruptibility_list = []
responding_list = []
timing_list = []
IOS_list = []
URCS_list = []
dependence_list = []
mobile_maintainace_list = []
answering_expectation_list = []
obligation_to_answer_list = []
Personal_Big5_Extraversion_list = []
Personal_Big5_Agreeableness_list = []
Personal_Big5_Conscientiousness_list = []
Personal_Big5_Neuroticism_list = []
Personal_Big5_Openness_list = []
Personal_Loneliness_list = []
Personal_NeedToBelong_list = []


Correlation_list = [interruptibility_list,responding_list, timing_list, Personal_Big5_Extraversion_list, Personal_Big5_Agreeableness_list,Personal_Big5_Conscientiousness_list,Personal_Big5_Neuroticism_list,Personal_Big5_Openness_list,Personal_Loneliness_list,Personal_NeedToBelong_list,IOS_list,URCS_list,dependence_list,mobile_maintainace_list,answering_expectation_list,obligation_to_answer_list]

with open('final.tsv') as f:
    reader = csv.DictReader(f, dialect='excel-tab')
    for row in reader:
        interruptibility = row['ESM_干擾']
        responding = row['ESM_預計回覆_code']
        timing = row['ESM_時機_code']
        IOS = row['Contact_IOS']
        URCS= row['Contact_URCS']
        dependence= row['Contact_Dependence']
        mobile_maintainace= row['Contact_MobileMaintainance']
        answering_expectation= row['Contact_AnsweringExpectation']
        obligation_to_answer= row['Contact_Obligation']

        Personal_Big5_Extraversion = row['Personal_Big5_Extraversion']
        Personal_Big5_Agreeableness = row['Personal_Big5_Agreeableness']
        Personal_Big5_Conscientiousness = row['Personal_Big5_Conscientiousness']
        Personal_Big5_Neuroticism = row['Personal_Big5_Neuroticism']
        Personal_Big5_Openness = row['Personal_Big5_Openness']
        Personal_Loneliness = row['Personal_Loneliness']
        Personal_NeedToBelong = row['Personal_NeedToBelong']



        if(interruptibility != "" and responding != "" and timing != "" and IOS != "" and responding != ""):
            interruptibility_list.append(float(interruptibility))
            responding_list.append(float(responding))
            timing_list.append(float(timing))
            IOS_list.append(float(IOS))
            URCS_list.append(float(URCS))
            dependence_list.append(float(dependence))
            mobile_maintainace_list.append(float(mobile_maintainace))
            answering_expectation_list.append(float(answering_expectation))
            obligation_to_answer_list.append(float(obligation_to_answer))
            Personal_Big5_Extraversion_list.append(float(Personal_Big5_Extraversion))
            Personal_Big5_Agreeableness_list.append(float(Personal_Big5_Agreeableness))
            Personal_Big5_Conscientiousness_list.append(float(Personal_Big5_Conscientiousness))
            Personal_Big5_Neuroticism_list.append(float(Personal_Big5_Neuroticism))
            Personal_Big5_Openness_list.append(float(Personal_Big5_Openness))
            Personal_Loneliness_list.append(float(Personal_Loneliness))
            Personal_NeedToBelong_list.append(float(Personal_NeedToBelong))




print("Interruptibility   Responding   Timing   Extraversion   Agreeableness   Conscientiousness   Neuroticism   Openness   Loneliness   NeedToBelong   IOS   URCS   Depandance   Mobile_maintainace   Answering_expectation   Obligation_to_answer_list")

for a in Correlation_list:
    for b in Correlation_list:
        print("%6.3f(%6.4f)" %(stats.pearsonr(a, b)[0], stats.pearsonr(a, b)[1]), end="  ")
    print("|")
