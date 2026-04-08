from rouge_score import rouge_scorer
from rag_studienordnung_assistent import rag_system

scorer = rouge_scorer.RougeScorer(['rougeL'])

expected_answers = [
    "Für das Praktikum müssen 60 ECTS erbracht werden.",
    "Das Studium dauert 6 Fachsemester.",
    "Ziele sind: (1) Fachwissen, (2) Methodenkompetenz, (3) Sozialkompetenz"
]

questions = [
    "Wie viele ECTS für Praktikum?",
    "Wie viele Fachsemester?",
    "Welche Ziele?"
]

for question, expected in zip(questions, expected_answers):
    model_answer = rag_system.answer_question(question,top_k=3, use_llm=True)
    scores = scorer.score(expected, model_answer)
    print(f"Q: {question}")
    print(f"A: {model_answer}")
    print(f"ROUGE-L: {scores['rougeL'].fmeasure:.3f}")