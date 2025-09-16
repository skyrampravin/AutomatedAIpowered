# Day 4: Detailed Step-by-Step Instructions - AI Integration in Sandbox

## Important: Sandbox AI Development
**Continue building on your Day 3 sandbox environment.** This day focuses on integrating AI question generation using your OpenAI API while maintaining the sandbox development approach with file-based storage.

## Task 1: Review AI Integration Requirements (20 minutes)

### 1.1 Verify Sandbox AI Service Configuration
1. **Check your AI service setup in `env/.env.playground`**:
   ```bash
   # For OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   
   # OR for Azure OpenAI
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_azure_openai_key_here
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   ```

2. **Test basic connectivity in sandbox**:
   ```python
   # Create test file: test_ai_sandbox.py
   import openai
   import os
   from dotenv import load_dotenv
   
   # Load playground environment
   load_dotenv('env/.env.playground')
   
   # Test OpenAI connection
   try:
       openai.api_key = os.getenv('OPENAI_API_KEY')
       response = openai.ChatCompletion.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": "Hello, are you working for sandbox testing?"}],
           max_tokens=50
       )
       print("✅ AI connection successful:", response.choices[0].message.content)
   except Exception as e:
       print("❌ AI connection failed:", e)
   ```

### 1.2 Review Current Prompt System
1. **Open `src/prompts/chat/config.json`**:
   - Understand current AI model configuration
   - Review temperature, token limits, and other parameters
2. **Open `src/prompts/chat/skprompt.txt`**:
   - See current prompt template
   - Plan how to modify for question generation

### 1.3 Plan Sandbox Question Generation Approach
1. **Design question generation flow for sandbox**:
   ```
   Course Topic → AI Prompt → Generated Questions → Save to playground/questions/ → Validation
   ```
2. **Sandbox integration points**:
   - Trigger question generation via bot commands (for testing)
   - Store generated questions in `playground/questions/` directory
   - Mix generated questions with previously missed questions from `playground/progress/`

## Task 2: Create AI Question Generation System for Sandbox (45 minutes)

### 2.1 Create Question Generation Prompts for Sandbox
1. **Create `src/prompts/question_generation/`** directory
2. **Create `src/prompts/question_generation/config.json`**:
   ```json
   {
     "schema": 1.1,
     "description": "Generate MCQ questions for learning courses in sandbox environment",
     "type": "completion",
     "completion": {
         "completion_type": "chat",
         "include_history": false,
         "include_input": true,
         "max_input_tokens": 2000,
         "max_tokens": 1500,
         "temperature": 0.7,
         "top_p": 0.9,
         "presence_penalty": 0.0,
         "frequency_penalty": 0.3,
         "stop_sequences": []
     },
     "augmentation": {
         "augmentation_type": "None"
     }
   }
   ```

3. **Create `src/prompts/question_generation/skprompt.txt`**:
   ```
   You are an expert educational content creator specializing in creating multiple-choice questions for online learning.
   
   Generate {{question_count}} multiple-choice questions about {{topic}} for a {{difficulty}} level course on {{course_name}}.
   
   Requirements:
   1. Each question should have exactly 4 options (A, B, C, D)
   2. Only one correct answer per question
   3. Include a brief explanation for the correct answer
   4. Make questions practical and relevant to real-world scenarios
   5. Vary question difficulty within the specified level
   6. Avoid trick questions or overly complex wording
   
   Course Context: {{course_description}}
   Learning Objectives: {{learning_objectives}}
   
   Return the response in this exact JSON format:
   {
     "questions": [
       {
         "id": "unique_id_1",
         "question": "Question text here?",
         "options": {
           "A": "First option",
           "B": "Second option", 
           "C": "Third option",
           "D": "Fourth option"
         },
         "correct_answer": "A",
         "explanation": "Brief explanation of why this is correct",
         "topic": "{{topic}}",
         "difficulty": "{{difficulty}}",
         "day": {{day_number}}
       }
     ]
   }
   ```

4. **Create sandbox question generator** `src/question_generator.py`:
   ```python
   import json
   import os
   from typing import List, Dict
   from datetime import datetime
   import openai
   from dotenv import load_dotenv
   
   class SandboxQuestionGenerator:
       """AI-powered question generator for sandbox development"""
       
       def __init__(self, storage_dir: str = "playground"):
           self.storage_dir = storage_dir
           self.questions_dir = f"{storage_dir}/questions"
           os.makedirs(self.questions_dir, exist_ok=True)
           
           # Load playground environment
           load_dotenv('env/.env.playground')
           openai.api_key = os.getenv('OPENAI_API_KEY')
   ```

**Sandbox Benefit**: Questions are generated and stored locally for immediate testing and iteration.
           "D": "Fourth option"
         },
         "correct_answer": "A",
         "explanation": "Explanation of why this answer is correct",
         "topic": "{{topic}}",
         "difficulty": "{{difficulty}}"
       }
     ]
   }
   ```

### 2.2 Create Sandbox Question Generator Module
1. **Complete `src/question_generator.py`** for sandbox development:
   ```python
   import json
   import uuid
   from typing import List, Dict, Optional
   from datetime import datetime
   import openai
   import os
   from dotenv import load_dotenv
   
   class SandboxQuestionGenerator:
       def __init__(self, storage_dir: str = "playground"):
           self.storage_dir = storage_dir
           self.questions_dir = f"{storage_dir}/questions"
           os.makedirs(self.questions_dir, exist_ok=True)
           
           # Load playground environment
           load_dotenv('env/.env.playground')
           openai.api_key = os.getenv('OPENAI_API_KEY')
       
       def generate_daily_questions(
           self, 
           course_id: str, 
           topic: str, 
           day: int,
           count: int = 5
       ) -> List[Dict]:
           """Generate daily questions for sandbox testing"""
           try:
               prompt = self._build_question_prompt(course_id, topic, day, count)
               
               response = openai.ChatCompletion.create(
                   model="gpt-3.5-turbo",
                   messages=[{"role": "user", "content": prompt}],
                   max_tokens=1500,
                   temperature=0.7
               )
               
               # Parse JSON response
               content = response.choices[0].message.content
               questions_data = json.loads(content)
               questions = questions_data.get("questions", [])
               
               # Save to sandbox storage
               self._save_questions_to_sandbox(course_id, day, questions)
               
               return questions
               
           except Exception as e:
               print(f"Error generating questions: {e}")
               return self._get_fallback_questions(topic, day)
       
       def _build_question_prompt(self, course_id: str, topic: str, day: int, count: int) -> str:
           """Build prompt for question generation"""
           return f"""
           Generate {count} multiple-choice questions about {topic} for day {day} of a Python programming course.
           
           Requirements:
           1. Each question should have exactly 4 options (A, B, C, D)
           2. Only one correct answer per question
           3. Include a brief explanation for the correct answer
           4. Make questions practical and beginner-friendly
           5. Focus on {topic} fundamentals
           
           Return ONLY valid JSON in this exact format:
           {{
             "questions": [
               {{
                 "id": "python_day{day}_q1",
                 "question": "What is a variable in Python?",
                 "options": {{
                   "A": "A container for storing data values",
                   "B": "A function that returns data",
                   "C": "A loop structure",
                   "D": "A conditional statement"
                 }},
                 "correct_answer": "A",
                 "explanation": "A variable is a container that stores data values in Python.",
                 "topic": "{topic}",
                 "difficulty": "beginner",
                 "day": {day}
               }}
             ]
           }}
           """
       
       def _save_questions_to_sandbox(self, course_id: str, day: int, questions: List[Dict]):
           """Save generated questions to sandbox files"""
           questions_file = f"{self.questions_dir}/{course_id}_day_{day}.json"
           with open(questions_file, 'w') as f:
               json.dump({
                   "course_id": course_id,
                   "day": day,
                   "generated_at": datetime.now().isoformat(),
                   "questions": questions
               }, f, indent=2)
       
       def _get_fallback_questions(self, topic: str, day: int) -> List[Dict]:
           """Provide fallback questions if AI generation fails"""
           return [
               {
                   "id": f"fallback_day{day}_q1",
                   "question": f"What is the main concept of {topic} in Python?",
                   "options": {
                       "A": "It's a fundamental concept",
                       "B": "It's an advanced feature",
                       "C": "It's optional to learn",
                       "D": "It's deprecated"
                   },
                   "correct_answer": "A",
                   "explanation": f"{topic} is a fundamental concept in Python programming.",
                   "topic": topic,
                   "difficulty": "beginner",
                   "day": day
               }
           ]
   ```

**Sandbox Testing**: This allows immediate question generation and local storage for testing.
           new_topic: str,
           wrong_questions: List[Dict],
           total_count: int = 10
       ) -> List[Dict]:
           """Generate new questions mixed with previously wrong answers"""
           pass
       
       def _format_question(self, question_data: Dict, question_id: str = None) -> Dict:
           """Format question to standard structure"""
           pass
       
       def _validate_question(self, question: Dict) -> bool:
           """Validate question structure and content"""
           pass
   ```

### 2.3 Implement Question Generation Logic
1. **Complete the QuestionGenerator class**:
   ```python
   async def generate_daily_questions(self, course_id: str, topic: str, difficulty: str = "intermediate", count: int = 10) -> List[Dict]:
       try:
           course_info = AVAILABLE_COURSES.get(course_id, {})
           
           # Prepare prompt variables
           prompt_vars = {
               "question_count": count,
               "topic": topic,
               "difficulty": difficulty,
               "course_name": course_info.get("name", course_id),
               "course_description": course_info.get("description", ""),
               "learning_objectives": ", ".join(course_info.get("topics", []))
           }
           
           # Generate questions using AI
           response = await self.prompts.render_template(
               "question_generation",
               self.model,
               prompt_vars
           )
           
           # Parse and validate response
           questions_data = json.loads(response)
           questions = []
           
           for q in questions_data.get("questions", []):
               question = self._format_question(q)
               if self._validate_question(question):
                   questions.append(question)
           
           return questions[:count]  # Ensure we don't exceed requested count
           
       except Exception as e:
           print(f"Error generating questions: {e}")
           return []
   ```

## Task 3: Implement Daily Quiz Logic (40 minutes)

### 3.1 Create Quiz Manager
1. **Create `src/quiz_manager.py`**:
   ```python
   from typing import List, Dict, Optional
   from datetime import datetime, timedelta
   import random
   
   from question_generator import QuestionGenerator
   from storage import SimpleStorage
   from courses import AVAILABLE_COURSES
   
   class QuizManager:
       def __init__(self):
           self.storage = SimpleStorage()
           self.question_generator = QuestionGenerator()
       
       async def prepare_daily_quiz(self, user_id: str) -> Optional[List[Dict]]:
           """Prepare daily quiz for a user"""
           pass
       
       def _get_daily_topic(self, course_id: str, day: int) -> str:
           """Get topic for specific day of course"""
           pass
       
       def _mix_questions(self, new_questions: List[Dict], wrong_questions: List[Dict], total_count: int = 10) -> List[Dict]:
           """Mix new questions with previously wrong answers"""
           pass
       
       async def start_daily_quiz(self, user_id: str) -> Dict:
           """Start daily quiz for user"""
           pass
       
       def get_quiz_status(self, user_id: str, day: int) -> Dict:
           """Get current quiz status for user"""
           pass
   ```

### 3.2 Implement Topic Progression
1. **Add topic progression logic**:
   ```python
   def _get_daily_topic(self, course_id: str, day: int) -> str:
       """Get topic for specific day of course"""
       course_info = AVAILABLE_COURSES.get(course_id, {})
       topics = course_info.get("topics", ["General"])
       
       # Cycle through topics over 30 days
       if not topics:
           return "General"
       
       # Distribute topics evenly over 30 days
       topic_index = (day - 1) % len(topics)
       return topics[topic_index]
   
   def _get_difficulty_progression(self, day: int) -> str:
       """Get difficulty level based on day"""
       if day <= 10:
           return "beginner"
       elif day <= 20:
           return "intermediate"
       else:
           return "advanced"
   ```

### 3.3 Implement Question Mixing Logic
1. **Add question mixing algorithm**:
   ```python
   def _mix_questions(self, new_questions: List[Dict], wrong_questions: List[Dict], total_count: int = 10) -> List[Dict]:
       """Mix new questions with previously wrong answers"""
       mixed_questions = []
       
       # Prioritize wrong questions (up to 40% of total)
       max_wrong = min(len(wrong_questions), int(total_count * 0.4))
       mixed_questions.extend(random.sample(wrong_questions, max_wrong))
       
       # Fill remaining with new questions
       remaining_count = total_count - len(mixed_questions)
       if len(new_questions) >= remaining_count:
           mixed_questions.extend(random.sample(new_questions, remaining_count))
       else:
           mixed_questions.extend(new_questions)
       
       # Shuffle final order
       random.shuffle(mixed_questions)
       return mixed_questions
   ```

## Task 4: Create Adaptive Cards for MCQs (35 minutes)

### 4.1 Design Adaptive Card Template
1. **Create `src/adaptive_cards.py`**:
   ```python
   from typing import List, Dict
   
   class AdaptiveCardBuilder:
       @staticmethod
       def create_quiz_card(questions: List[Dict], quiz_id: str, user_id: str) -> Dict:
           """Create adaptive card for multiple choice quiz"""
           pass
       
       @staticmethod
       def create_question_block(question: Dict, question_index: int) -> Dict:
           """Create a single question block"""
           pass
       
       @staticmethod
       def create_result_card(results: Dict) -> Dict:
           """Create result card showing quiz performance"""
           pass
       
       @staticmethod
       def create_progress_card(user_progress: Dict) -> Dict:
           """Create progress summary card"""
           pass
   ```

### 4.2 Implement Quiz Card Template
1. **Create adaptive card structure for questions**:
   ```python
   @staticmethod
   def create_quiz_card(questions: List[Dict], quiz_id: str, user_id: str) -> Dict:
       card = {
           "type": "AdaptiveCard",
           "version": "1.3",
           "body": [
               {
                   "type": "TextBlock",
                   "text": f"📝 Daily Quiz - {len(questions)} Questions",
                   "weight": "Bolder",
                   "size": "Large"
               },
               {
                   "type": "TextBlock",
                   "text": "Select the best answer for each question:",
                   "wrap": True
               }
           ],
           "actions": []
       }
       
       # Add each question as a block
       for i, question in enumerate(questions):
           question_block = AdaptiveCardBuilder.create_question_block(question, i)
           card["body"].extend(question_block)
       
       # Add submit action
       card["actions"].append({
           "type": "Action.Submit",
           "title": "Submit Answers",
           "data": {
               "action": "submit_quiz",
               "quiz_id": quiz_id,
               "user_id": user_id
           }
       })
       
       return card
   ```

### 4.3 Implement Question Block Structure
1. **Create individual question blocks**:
   ```python
   @staticmethod
   def create_question_block(question: Dict, question_index: int) -> List[Dict]:
       question_block = [
           {
               "type": "TextBlock",
               "text": f"**Question {question_index + 1}:** {question['question']}",
               "wrap": True,
               "spacing": "Medium"
           },
           {
               "type": "Input.ChoiceSet",
               "id": f"question_{question_index}",
               "choices": [
                   {"title": f"{key}: {value}", "value": key}
                   for key, value in question["options"].items()
               ],
               "style": "expanded",
               "isRequired": True
           }
       ]
       return question_block
   ```

## Task 5: Integrate Quiz System with Bot (30 minutes)

### 5.1 Add Quiz Commands to Bot
1. **Update `src/bot.py` with quiz functionality**:
   ```python
   from quiz_manager import QuizManager
   from adaptive_cards import AdaptiveCardBuilder
   
   # Initialize quiz manager
   quiz_manager = QuizManager()
   
   @bot_app.message("/start_quiz")
   async def on_start_quiz_command(context: TurnContext, state: TurnState):
       user_id = context.activity.from_property.id
       
       # Check if user is enrolled
       enrollment = storage.get_enrollment(user_id)
       if not enrollment:
           await context.send_activity("❌ You need to enroll in a course first. Use `/enroll [course_name]`")
           return
       
       # Generate and send daily quiz
       quiz_result = await quiz_manager.start_daily_quiz(user_id)
       
       if quiz_result.get("success"):
           quiz_card = AdaptiveCardBuilder.create_quiz_card(
               quiz_result["questions"],
               quiz_result["quiz_id"],
               user_id
           )
           
           await context.send_activity(MessageFactory.attachment(
               CardFactory.adaptive_card(quiz_card)
           ))
       else:
           await context.send_activity(f"❌ {quiz_result.get('error', 'Failed to generate quiz')}")
   ```

### 5.2 Handle Quiz Submissions
1. **Add submission handler**:
   ```python
   @bot_app.adaptive_card_invoke("submit_quiz")
   async def on_quiz_submit(context: TurnContext, state: TurnState):
       user_id = context.activity.from_property.id
       submission_data = context.activity.value
       
       # Process quiz answers
       results = await quiz_manager.process_quiz_submission(user_id, submission_data)
       
       # Send results
       result_card = AdaptiveCardBuilder.create_result_card(results)
       await context.send_activity(MessageFactory.attachment(
           CardFactory.adaptive_card(result_card)
       ))
       
       # Update user progress
       await quiz_manager.update_user_progress(user_id, results)
   ```

### 5.3 Add Quiz Status Command
1. **Add status checking**:
   ```python
   @bot_app.message("/quiz_status")
   async def on_quiz_status_command(context: TurnContext, state: TurnState):
       user_id = context.activity.from_property.id
       
       enrollment = storage.get_enrollment(user_id)
       if not enrollment:
           await context.send_activity("❌ You are not enrolled in any course.")
           return
       
       status = quiz_manager.get_quiz_status(user_id, enrollment.current_day)
       progress_card = AdaptiveCardBuilder.create_progress_card(status)
       
       await context.send_activity(MessageFactory.attachment(
           CardFactory.adaptive_card(progress_card)
       ))
   ```

## Task 6: Test AI Question Generation (25 minutes)

### 6.1 Test Question Generation
1. **Create test script `test_questions.py`**:
   ```python
   import asyncio
   from question_generator import QuestionGenerator
   
   async def test_question_generation():
       generator = QuestionGenerator()
       
       # Test basic question generation
       questions = await generator.generate_daily_questions(
           course_id="python-basics",
           topic="Variables",
           difficulty="beginner",
           count=3
       )
       
       print(f"Generated {len(questions)} questions:")
       for i, q in enumerate(questions, 1):
           print(f"\nQuestion {i}: {q['question']}")
           for key, value in q['options'].items():
               marker = "✓" if key == q['correct_answer'] else " "
               print(f"  {marker} {key}: {value}")
           print(f"  Explanation: {q['explanation']}")
   
   if __name__ == "__main__":
       asyncio.run(test_question_generation())
   ```

### 6.2 Test in Teams Environment
1. **Deploy updated code**:
   ```powershell
   # Deploy to Azure
   teamsfx deploy
   ```

2. **Test quiz commands in Teams**:
   - Send `/start_quiz` command
   - Verify adaptive cards display correctly
   - Test question submission and results
   - Check progress tracking

### 6.3 Validate Question Quality
1. **Review generated questions for**:
   - Correct JSON format
   - Appropriate difficulty level
   - Clear and unambiguous options
   - Accurate explanations
   - Relevant to course topic

## Task 4: Test Sandbox AI Question Generation (20 minutes)

### 4.1 Test Question Generation in Sandbox
1. **Create test script** `test_question_generation.py`:
   ```python
   from question_generator import SandboxQuestionGenerator
   from dotenv import load_dotenv
   
   # Load playground environment
   load_dotenv('env/.env.playground')
   
   # Test question generation
   generator = SandboxQuestionGenerator("playground")
   
   print("Testing AI question generation...")
   questions = generator.generate_daily_questions(
       course_id="python-basics",
       topic="Variables",
       day=1,
       count=2
   )
   
   print(f"Generated {len(questions)} questions:")
   for i, q in enumerate(questions, 1):
       print(f"\nQuestion {i}: {q['question']}")
       print(f"Correct Answer: {q['correct_answer']}")
       print(f"Explanation: {q['explanation']}")
   ```

2. **Run the test**:
   ```powershell
   cd src
   python test_question_generation.py
   ```

3. **Verify sandbox storage**:
   - Check `playground/questions/` directory for generated JSON files
   - Inspect question quality and format
   - Verify JSON structure is correct

### 4.2 Test Bot Integration in Sandbox
1. **Start the bot locally** (if not already running):
   ```powershell
   # Ensure playground environment
   $env:ENVIRONMENT = "playground"
   cd src
   python app.py
   ```

2. **Test in sandbox Teams**:
   - Send `/enroll` to ensure you're enrolled
   - Send `/generate` to test question generation
   - Send `/quiz` to test quiz delivery
   - Verify questions are relevant and well-formatted

3. **Check sandbox storage**:
   - Verify `playground/enrollments.json` is updated
   - Check `playground/questions/` for generated questions
   - Ensure data persists between bot sessions

### 4.3 Iterate on Question Quality
1. **Review generated questions for**:
   - Clear, unambiguous wording
   - Appropriate difficulty level
   - Accurate correct answers
   - Helpful explanations
   - Relevant to course topic

2. **Refine prompts if needed**:
   - Update `src/prompts/question_generation/skprompt.txt`
   - Adjust temperature and other parameters
   - Test with different topics

**Sandbox Advantage**: Immediate feedback loop for prompt refinement without deploying to Azure.

## Task 5: Prepare for Day 5 Answer Processing (15 minutes)

### 5.1 Plan Sandbox Answer Evaluation
1. **Design answer processing for sandbox**:
   - Store user answers in `playground/progress/{user_id}_day{day}.json`
   - Simple scoring mechanism (correct/incorrect)
   - Track wrong answers for re-asking

2. **Plan progress tracking enhancements**:
   - Daily progress summaries
   - Overall course progress
   - Simple streak tracking

### 5.2 Document Day 4 Sandbox Progress
1. **Create status report**:
   ```
   Day 4 Sandbox Completion Status:
   - AI question generation: [WORKING/ISSUES]
   - Sandbox storage: [COMPLETE/PARTIAL]
   - Bot command integration: [WORKING/ISSUES]
   - Teams sandbox testing: [SUCCESSFUL/FAILED]
   - Ready for answer processing: [YES/NO]
   
   Generated Questions Quality:
   - Clear wording: [GOOD/NEEDS_WORK]
   - Appropriate difficulty: [GOOD/NEEDS_WORK]
   - Accurate answers: [VERIFIED/NEEDS_CHECK]
   ```

---

## Important Notes:
- **Sandbox Development** - All AI integration can be tested without Azure infrastructure
- **API Cost Management** - Use small question counts during development to manage OpenAI costs
- **Local Storage** - Questions and progress stored in JSON files for easy inspection
- **Error Handling** - Fallback questions ensure bot always works even if AI fails
- **Iterative Development** - Easy to refine prompts and test immediately in sandbox

## Common Issues:
- **AI API quota limits**: Monitor usage during development
- **JSON parsing errors**: Add robust error handling for AI responses
- **Environment variables**: Ensure `env/.env.playground` has correct OpenAI key
- **File permissions**: Check that playground directory is writable
- **Question quality**: Review and refine prompts based on generated content

## Success Criteria:
- ✅ AI successfully generates contextual MCQs in sandbox
- ✅ Questions are properly formatted and stored locally
- ✅ Bot commands work in sandbox Teams environment
- ✅ Question generation is reliable and cost-effective
- ✅ Ready for answer evaluation and progress tracking on Day 5

**Total estimated time: 2-2.5 hours (sandbox development)**

---
## Sandbox Mode Notes
| Aspect | Sandbox Advantage |
|--------|------------------|
| **Development Speed** | Test AI integration immediately without deploying to Azure. Local storage allows instant feedback. |
| **Cost Management** | Generate small batches of questions during development. Easy to monitor and control API usage. |
| **Quality Control** | Inspect generated questions in JSON files. Iterate on prompts without deployment overhead. |
| **Error Testing** | Test fallback mechanisms locally. Ensure bot works even when AI generation fails. |
| **Rapid Iteration** | Modify prompts and test immediately. No deployment delays for testing changes. |

**Next Steps**: Day 5 will add answer processing and progress tracking while continuing to use the sandbox environment for rapid development and testing.