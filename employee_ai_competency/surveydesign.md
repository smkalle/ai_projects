# AI Competency Survey Design v2.0

This document outlines the design and implementation of the AI Competency Survey with separated input questions and competency verdicts.

## 1. Project Goal

The primary goal is to create a dynamic, web-based survey that helps individuals self-assess their AI competency through neutral questions, separate from the final competency level verdicts. The survey provides objective assessment questions while delivering personalized competency level results.

## 2. Key Design Principles

### Input vs. Verdict Separation
- **Input Questions**: Neutral, behavioral assessment questions that users answer
- **Verdict Labels**: Competency level determinations (Foundational, Developing, Proficient, Advanced) shown only in results
- **Clear Distinction**: Users answer "How often do you..." not "I am at the Unacceptable level"

### Role-Specific Customization
Each role has tailored questions focusing on relevant AI use cases:
- **Engineering**: Code generation, debugging, workflow integration
- **Product**: Strategy development, user research, feature planning
- **Support**: Customer interaction automation, workflow optimization
- **People/HR**: Recruitment processes, onboarding, policy development
- **Marketing**: Content creation, audience analysis, campaign optimization

## 3. Updated Architecture

### Core Components
*   **`index.html`**: Modern multi-step survey interface with progress tracking
*   **`styles.css`**: Silicon Valley tech company styling with role-specific visual elements
*   **`script.js`**: Enhanced logic with separate question generation and verdict calculation
*   **`surveydesign.md`**: This design documentation
*   **`ai_competency_gradation.md`**: Competency matrix for verdict mapping

### Data Structure
```javascript
// Questions are separate from competency descriptions
const roleQuestions = {
  'Engineering': [
    { id: 'freq_ai_tools', question: 'How often do you use AI coding assistants?', options: [...] },
    { id: 'workflow_integration', question: 'How integrated are AI tools in your development workflow?', options: [...] }
  ]
}

// Verdicts map scores to competency levels
const competencyLevels = {
  'Foundational': { range: [0, 25], description: '...' },
  'Developing': { range: [26, 50], description: '...' },
  'Proficient': { range: [51, 75], description: '...' },
  'Advanced': { range: [76, 100], description: '...' }
}
```

## 4. Enhanced User Flow

### Step 1: Role Selection
- Visual role cards with icons and descriptions
- Context-specific information about AI competency for that role
- Progress indicator showing current step

### Step 2: Assessment Questions
- 5-7 role-specific questions per role
- Multiple choice answers with scoring (0-4 points each)
- Questions focus on frequency, complexity, and impact of AI usage
- No mention of competency levels during assessment

### Step 3: Results & Verdict
- Calculated competency level based on total score
- Personalized description of current capabilities
- Growth opportunities and next steps
- Option to retake or share results

## 5. Question Design Framework

### Question Types
1. **Frequency Questions**: "How often do you use AI for [specific task]?"
2. **Complexity Questions**: "What level of AI integration have you achieved?"
3. **Impact Questions**: "How has AI affected your work efficiency/quality?"
4. **Knowledge Questions**: "How familiar are you with [AI concept/tool]?"

### Scoring Scale (0-4 points)
- **0 Points**: Never/Not at all/Unfamiliar
- **1 Point**: Rarely/Basic level/Somewhat familiar
- **2 Points**: Sometimes/Intermediate/Moderately familiar
- **3 Points**: Often/Advanced/Very familiar
- **4 Points**: Always/Expert level/Extremely familiar

### Competency Level Mapping
- **Foundational (0-25%)**: Basic awareness, minimal usage
- **Developing (26-50%)**: Regular usage for simple tasks
- **Proficient (51-75%)**: Advanced usage with workflow integration
- **Advanced (76-100%)**: Expert usage driving innovation

## 6. Technical Implementation

### Frontend Features
- **Progressive Enhancement**: Works without JavaScript for accessibility
- **Responsive Design**: Mobile-first approach with touch-friendly interfaces
- **Accessibility**: WCAG 2.1 AA compliance with keyboard navigation
- **Performance**: Optimized loading with minimal external dependencies

### Data Collection
- **Anonymous**: No personal data collection by default
- **Optional Analytics**: Aggregated usage patterns for improvement
- **Export Options**: Results can be saved/shared in multiple formats

## 7. Future Enhancements

### Phase 2 Features
*   **Multi-language Support**: Internationalization for global teams
*   **Team Dashboards**: Aggregate team competency insights
*   **Learning Pathways**: Personalized AI skill development recommendations
*   **Integration APIs**: Connect with HR systems and learning platforms

### Advanced Features
*   **Adaptive Questioning**: Dynamic question selection based on previous answers
*   **Competency Tracking**: Progress monitoring over time
*   **Peer Comparison**: Anonymous benchmarking against similar roles
*   **Certification Paths**: Integration with AI skill certification programs

## 8. Success Metrics

### User Experience
- Completion rate > 85%
- Average completion time < 5 minutes
- User satisfaction score > 4.2/5

### Business Impact
- Increased AI tool adoption across teams
- Improved identification of training needs
- Better resource allocation for AI initiatives
- Enhanced team competency visibility