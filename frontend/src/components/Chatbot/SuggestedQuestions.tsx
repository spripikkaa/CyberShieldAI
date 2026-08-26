const DEFAULT_QUESTIONS = [
  "What is phishing?",
  "How do I use CyberShield AI?",
  "What is SSL?",
  "What is DNS?",
  "How do I stay safe online?",
  "What is ransomware?",
];

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
  questions?: string[];
}

export default function SuggestedQuestions({
  onSelect,
  questions = DEFAULT_QUESTIONS,
}: SuggestedQuestionsProps) {
  return (
    <div className="cs-suggested">
      <p className="cs-suggested__label">Try asking:</p>
      <div className="cs-suggested__chips">
        {questions.map((question) => (
          <button
            key={question}
            type="button"
            className="cs-suggested__chip"
            onClick={() => onSelect(question)}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
