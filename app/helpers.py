from flask_login import current_user
from app.models import ContactQuestionnaire

def find_questionnaire(current_user, questionnaire_id):
	questionnaires = ContactQuestionnaire.query.filter_by(user_id=current_user.id).all()
	for questionnaire in questionnaires:
		if questionnaire_id == questionnaire.id:
			return 0, "Found", questionnaire
	return 2, "you don't have THIS contact", None