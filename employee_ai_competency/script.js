document.addEventListener('DOMContentLoaded', () => {
    // Role-specific assessment questions (neutral, behavioral)
    const roleQuestions = {
        'Engineering': [
            {
                id: 'ai_tool_frequency',
                question: 'How often do you use AI coding assistants (like GitHub Copilot, ChatGPT, Claude) in your development work?',
                options: [
                    { text: 'Never or almost never', score: 0 },
                    { text: 'A few times per month', score: 1 },
                    { text: 'A few times per week', score: 2 },
                    { text: 'Daily for specific tasks', score: 3 },
                    { text: 'Multiple times daily as core workflow', score: 4 }
                ]
            },
            {
                id: 'code_review_ai',
                question: 'How do you handle AI-generated code in your workflow?',
                options: [
                    { text: "I don't use AI-generated code", score: 0 },
                    { text: 'I use it rarely and always manually review line by line', score: 1 },
                    { text: 'I use it occasionally with careful review and testing', score: 2 },
                    { text: 'I use it regularly with systematic review processes', score: 3 },
                    { text: 'I use it extensively with automated review and security checks', score: 4 }
                ]
            },
            {
                id: 'ai_workflow_integration',
                question: 'How integrated are AI tools in your development workflow?',
                options: [
                    { text: 'Not integrated - I rely on traditional methods', score: 0 },
                    { text: 'Minimal integration for simple tasks like syntax help', score: 1 },
                    { text: 'Moderate integration for code generation and debugging', score: 2 },
                    { text: 'High integration with chained AI interactions and automation', score: 3 },
                    { text: 'Complete integration with AI-first development pipeline', score: 4 }
                ]
            },
            {
                id: 'ai_tools_knowledge',
                question: 'How familiar are you with different AI development tools and their capabilities?',
                options: [
                    { text: 'Not familiar with AI development tools', score: 0 },
                    { text: 'Know basic tools like ChatGPT for coding questions', score: 1 },
                    { text: 'Familiar with multiple tools (Copilot, Claude, etc.)', score: 2 },
                    { text: 'Know advanced tools and can choose best tool for each task', score: 3 },
                    { text: 'Expert knowledge of AI tools, contribute to tool development', score: 4 }
                ]
            },
            {
                id: 'ai_impact_delivery',
                question: 'What impact has AI had on your development velocity and code quality?',
                options: [
                    { text: 'No noticeable impact on my work', score: 0 },
                    { text: 'Slight improvement in productivity for specific tasks', score: 1 },
                    { text: 'Moderate improvement in both speed and quality', score: 2 },
                    { text: 'Significant improvement with measurable metrics', score: 3 },
                    { text: 'Transformational impact - fundamentally changed how I work', score: 4 }
                ]
            }
        ],
        'Product': [
            {
                id: 'ai_product_usage',
                question: 'How often do you use AI tools for product management tasks (research, documentation, analysis)?',
                options: [
                    { text: 'Never or almost never', score: 0 },
                    { text: 'Occasionally for document drafting', score: 1 },
                    { text: 'Regularly for research and synthesis', score: 2 },
                    { text: 'Daily for multiple product tasks', score: 3 },
                    { text: 'Continuously integrated into all product workflows', score: 4 }
                ]
            },
            {
                id: 'ai_strategy_planning',
                question: 'How do you incorporate AI considerations into product strategy and roadmap planning?',
                options: [
                    { text: "I don't consider AI in product planning", score: 0 },
                    { text: 'I occasionally discuss AI features as possibilities', score: 1 },
                    { text: 'I regularly evaluate AI opportunities for our product', score: 2 },
                    { text: 'AI capabilities are central to our product strategy', score: 3 },
                    { text: 'I lead industry innovation in AI-first product experiences', score: 4 }
                ]
            },
            {
                id: 'ai_user_research',
                question: 'How do you use AI in user research and data analysis?',
                options: [
                    { text: 'I conduct all research and analysis manually', score: 0 },
                    { text: 'I use AI occasionally for summarizing user feedback', score: 1 },
                    { text: 'I regularly use AI for data synthesis and insight generation', score: 2 },
                    { text: 'I use AI extensively for predictive user behavior analysis', score: 3 },
                    { text: 'I build AI-powered research and analytics systems', score: 4 }
                ]
            },
            {
                id: 'ai_feature_evaluation',
                question: 'How do you evaluate and measure AI feature performance and ROI?',
                options: [
                    { text: "I don't work with AI features", score: 0 },
                    { text: 'I use basic metrics to track AI feature usage', score: 1 },
                    { text: 'I have established KPIs for AI feature performance', score: 2 },
                    { text: 'I use sophisticated measurement frameworks with A/B testing', score: 3 },
                    { text: 'I pioneer new methodologies for AI product measurement', score: 4 }
                ]
            },
            {
                id: 'ai_technical_collaboration',
                question: 'How effectively do you collaborate with technical teams on AI implementation?',
                options: [
                    { text: 'I have minimal involvement in technical AI discussions', score: 0 },
                    { text: 'I can communicate basic AI requirements to engineers', score: 1 },
                    { text: 'I understand AI capabilities and constraints for planning', score: 2 },
                    { text: 'I actively contribute to AI architecture and model selection', score: 3 },
                    { text: 'I lead cross-functional AI initiatives and technical decisions', score: 4 }
                ]
            }
        ],
        'Support': [
            {
                id: 'ai_support_tools',
                question: 'How often do you use AI tools for customer support tasks?',
                options: [
                    { text: 'Never - I handle all tickets manually', score: 0 },
                    { text: 'Occasionally for drafting responses', score: 1 },
                    { text: 'Regularly for ticket summarization and responses', score: 2 },
                    { text: 'Daily for multiple support workflows', score: 3 },
                    { text: 'AI is fully integrated into all support processes', score: 4 }
                ]
            },
            {
                id: 'ai_workflow_automation',
                question: 'How have you automated support workflows using AI?',
                options: [
                    { text: 'No automation - all processes are manual', score: 0 },
                    { text: 'Basic automation for simple, repetitive tasks', score: 1 },
                    { text: 'Moderate automation with tools like Zapier + AI', score: 2 },
                    { text: 'Advanced automation with custom AI workflows', score: 3 },
                    { text: 'Built comprehensive AI-powered support systems', score: 4 }
                ]
            },
            {
                id: 'ai_customer_interaction',
                question: 'How do you use AI to improve customer interaction quality?',
                options: [
                    { text: 'All customer interactions are handled without AI assistance', score: 0 },
                    { text: 'I use AI occasionally to help draft better responses', score: 1 },
                    { text: 'I regularly use AI to personalize and improve responses', score: 2 },
                    { text: 'I use AI for real-time assistance during customer calls/chats', score: 3 },
                    { text: 'I deploy AI systems that proactively improve customer experience', score: 4 }
                ]
            },
            {
                id: 'ai_metrics_analysis',
                question: 'How do you use AI for support metrics analysis and optimization?',
                options: [
                    { text: 'I track basic metrics manually without AI assistance', score: 0 },
                    { text: 'I use AI occasionally to analyze support trends', score: 1 },
                    { text: 'I regularly use AI for performance tracking and insights', score: 2 },
                    { text: 'I build AI dashboards for predictive support analytics', score: 3 },
                    { text: 'I create AI systems that automatically optimize support operations', score: 4 }
                ]
            },
            {
                id: 'ai_knowledge_management',
                question: 'How do you leverage AI for knowledge management and training?',
                options: [
                    { text: 'All knowledge management is manual and static', score: 0 },
                    { text: 'I use AI occasionally to create or update documentation', score: 1 },
                    { text: 'I regularly use AI to maintain and improve knowledge bases', score: 2 },
                    { text: 'I use AI to create dynamic, personalized training content', score: 3 },
                    { text: 'I build AI systems that automatically update and optimize knowledge', score: 4 }
                ]
            }
        ],
        'People / HR': [
            {
                id: 'ai_recruitment',
                question: 'How do you use AI in recruitment and hiring processes?',
                options: [
                    { text: 'All recruitment processes are manual', score: 0 },
                    { text: 'I use AI occasionally for job description writing', score: 1 },
                    { text: 'I regularly use AI for candidate screening and interview prep', score: 2 },
                    { text: 'I have implemented AI-enhanced recruitment workflows', score: 3 },
                    { text: 'I have transformed recruitment with comprehensive AI systems', score: 4 }
                ]
            },
            {
                id: 'ai_employee_onboarding',
                question: 'How do you use AI for employee onboarding and development?',
                options: [
                    { text: 'Onboarding and development are entirely manual processes', score: 0 },
                    { text: 'I use AI occasionally for creating onboarding materials', score: 1 },
                    { text: 'I regularly use AI for personalized onboarding experiences', score: 2 },
                    { text: 'I have built AI-powered learning and development systems', score: 3 },
                    { text: 'I lead innovation in AI-driven employee experience platforms', score: 4 }
                ]
            },
            {
                id: 'ai_policy_compliance',
                question: 'How do you handle AI ethics, privacy, and compliance in HR processes?',
                options: [
                    { text: 'I am not familiar with AI compliance requirements', score: 0 },
                    { text: 'I understand basic privacy limitations of AI tools', score: 1 },
                    { text: 'I actively ensure compliance and ethical AI usage', score: 2 },
                    { text: 'I develop and enforce comprehensive AI policies', score: 3 },
                    { text: 'I lead industry standards for ethical AI in HR', score: 4 }
                ]
            },
            {
                id: 'ai_data_analysis',
                question: 'How do you use AI for HR data analysis and insights?',
                options: [
                    { text: 'All HR analysis is done manually with basic tools', score: 0 },
                    { text: 'I use AI occasionally for simple data summarization', score: 1 },
                    { text: 'I regularly use AI for employee sentiment and performance analysis', score: 2 },
                    { text: 'I build predictive models for retention and performance', score: 3 },
                    { text: 'I create advanced AI systems for workforce optimization', score: 4 }
                ]
            },
            {
                id: 'ai_team_enablement',
                question: 'How do you enable and train others in your organization to use AI effectively?',
                options: [
                    { text: 'I do not provide AI training or guidance to others', score: 0 },
                    { text: 'I occasionally share basic AI tool recommendations', score: 1 },
                    { text: 'I regularly conduct AI training sessions and create guidelines', score: 2 },
                    { text: 'I design comprehensive AI enablement programs', score: 3 },
                    { text: 'I lead organizational transformation in AI adoption', score: 4 }
                ]
            }
        ],
        'Marketing': [
            {
                id: 'ai_content_creation',
                question: 'How often do you use AI for content creation and marketing materials?',
                options: [
                    { text: 'Never - all content is created manually', score: 0 },
                    { text: 'Occasionally for brainstorming and first drafts', score: 1 },
                    { text: 'Regularly for various content types with human editing', score: 2 },
                    { text: 'Daily with sophisticated prompting and brand consistency', score: 3 },
                    { text: 'AI is central to all content operations and strategy', score: 4 }
                ]
            },
            {
                id: 'ai_audience_analysis',
                question: 'How do you use AI for audience analysis and targeting?',
                options: [
                    { text: 'All audience analysis is done manually', score: 0 },
                    { text: 'I use AI occasionally for basic customer insights', score: 1 },
                    { text: 'I regularly use AI for audience segmentation and analysis', score: 2 },
                    { text: 'I use AI for predictive audience modeling and personalization', score: 3 },
                    { text: 'I build AI systems that automatically optimize targeting', score: 4 }
                ]
            },
            {
                id: 'ai_campaign_optimization',
                question: 'How do you use AI to optimize marketing campaigns and performance?',
                options: [
                    { text: 'Campaign optimization is entirely manual', score: 0 },
                    { text: 'I use AI occasionally for performance analysis', score: 1 },
                    { text: 'I regularly use AI for A/B testing and optimization', score: 2 },
                    { text: 'I use AI for real-time campaign adjustment and bidding', score: 3 },
                    { text: 'I have built fully automated AI-driven campaign systems', score: 4 }
                ]
            },
            {
                id: 'ai_customer_journey',
                question: 'How do you use AI to understand and optimize the customer journey?',
                options: [
                    { text: 'Customer journey analysis is done without AI assistance', score: 0 },
                    { text: 'I use AI occasionally to analyze customer behavior data', score: 1 },
                    { text: 'I regularly use AI for journey mapping and optimization', score: 2 },
                    { text: 'I use AI for predictive customer behavior and personalization', score: 3 },
                    { text: 'I create AI systems that automatically optimize customer experiences', score: 4 }
                ]
            },
            {
                id: 'ai_marketing_innovation',
                question: 'How do you drive AI innovation and adoption in marketing?',
                options: [
                    { text: 'I focus on traditional marketing methods', score: 0 },
                    { text: 'I occasionally experiment with new AI marketing tools', score: 1 },
                    { text: 'I regularly test and implement AI marketing innovations', score: 2 },
                    { text: 'I lead AI marketing initiatives and train other marketers', score: 3 },
                    { text: 'I pioneer new AI marketing methodologies and speak at industry events', score: 4 }
                ]
            }
        ]
    };

    // Competency level definitions (used only for results)
    const competencyLevels = {
        'Foundational': {
            range: [0, 25],
            title: 'Foundational',
            description: 'You have basic awareness of AI tools and capabilities but limited hands-on experience.',
            color: '#f56565',
            recommendations: [
                'Start experimenting with basic AI tools relevant to your role',
                'Take introductory courses on AI and its applications',
                'Join communities and forums focused on AI in your field',
                'Begin with simple, low-risk AI experiments'
            ]
        },
        'Developing': {
            range: [26, 50],
            title: 'Developing',
            description: 'You regularly use AI tools for basic tasks and understand their fundamental capabilities.',
            color: '#ed8936',
            recommendations: [
                'Expand your toolkit with more advanced AI applications',
                'Learn prompt engineering and optimization techniques',
                'Start measuring the impact of AI on your work efficiency',
                'Begin integrating AI tools into your daily workflows'
            ]
        },
        'Proficient': {
            range: [51, 75],
            title: 'Proficient',
            description: 'You have advanced AI skills with sophisticated workflow integration and measurable impact.',
            color: '#38b2ac',
            recommendations: [
                'Share your knowledge and mentor others in AI adoption',
                'Lead AI initiatives and pilot programs in your team',
                'Develop expertise in AI ethics and best practices',
                'Create documentation and training materials for others'
            ]
        },
        'Advanced': {
            range: [76, 100],
            title: 'Advanced',
            description: 'You are an AI expert driving innovation and transformation in your field.',
            color: '#48bb78',
            recommendations: [
                'Lead industry discussions and contribute to AI thought leadership',
                'Mentor other professionals and organizations in AI adoption',
                'Pioneer new AI applications and methodologies',
                'Speak at conferences and contribute to AI research'
            ]
        }
    };

    // Role context and customization data
    const roleContexts = {
        'Engineering': {
            icon: '💻',
            subtitle: 'Development & Technical',
            context: 'This assessment evaluates your current use of AI tools in software development workflows, from code generation to deployment automation.',
            focusAreas: ['Code generation and review', 'AI-assisted debugging', 'Development workflow integration', 'Security and best practices']
        },
        'Product': {
            icon: '🚀',
            subtitle: 'Strategy & Innovation',
            context: 'This assessment focuses on how you leverage AI for product strategy, user research, feature development, and cross-functional collaboration.',
            focusAreas: ['Strategic AI implementation', 'User experience enhancement', 'Market analysis and insights', 'ROI measurement and optimization']
        },
        'Support': {
            icon: '🎧',
            subtitle: 'Customer Experience',
            context: 'This assessment examines your use of AI for customer service automation, workflow optimization, and experience enhancement.',
            focusAreas: ['Automated customer interactions', 'Workflow optimization', 'Response quality improvement', 'Metrics and performance tracking']
        },
        'People / HR': {
            icon: '👥',
            subtitle: 'Human Resources',
            context: 'This assessment covers AI applications in recruitment, employee development, policy creation, and organizational enablement.',
            focusAreas: ['Recruitment and hiring efficiency', 'Employee onboarding automation', 'Policy development and compliance', 'Training and development programs']
        },
        'Marketing': {
            icon: '📈',
            subtitle: 'Growth & Engagement',
            context: 'This assessment evaluates your use of AI for content creation, audience analysis, campaign optimization, and marketing innovation.',
            focusAreas: ['Content generation and optimization', 'Audience analysis and targeting', 'Campaign automation', 'Performance measurement and growth']
        }
    };

    // Application state
    let currentStep = 1;
    let selectedRole = null;
    let currentQuestionIndex = 0;
    let responses = [];
    let assessmentComplete = false;

    // DOM elements
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const roleSection = document.getElementById('role-section');
    const surveySection = document.getElementById('survey-section');
    const resultsSection = document.getElementById('results-section');
    const roleGrid = document.getElementById('role-grid');
    const roleContext = document.getElementById('role-context');
    const surveyQuestions = document.getElementById('survey-questions');
    const resultDiv = document.getElementById('result');
    const backBtn = document.getElementById('back-btn');
    const continueBtn = document.getElementById('continue-btn');
    const submitBtn = document.getElementById('submit-btn');
    const retakeBtn = document.getElementById('retake-btn');
    const shareBtn = document.getElementById('share-btn');

    // Initialize the application
    init();

    function init() {
        populateRoleGrid();
        updateProgress();
        setupEventListeners();
    }

    function setupEventListeners() {
        backBtn.addEventListener('click', goBack);
        continueBtn.addEventListener('click', goNext);
        submitBtn.addEventListener('click', completeAssessment);
        retakeBtn.addEventListener('click', resetAssessment);
        shareBtn.addEventListener('click', shareResults);
    }

    function populateRoleGrid() {
        roleGrid.innerHTML = '';
        
        Object.keys(roleQuestions).forEach(role => {
            const context = roleContexts[role];
            if (!context) return;

            const roleCard = document.createElement('div');
            roleCard.className = 'role-card';
            roleCard.setAttribute('tabindex', '0');
            roleCard.setAttribute('role', 'button');
            roleCard.setAttribute('aria-label', `Select ${role} role`);
            
            roleCard.innerHTML = `
                <div class="role-icon">${context.icon}</div>
                <div class="role-title">${role}</div>
                <div class="role-subtitle">${context.subtitle}</div>
            `;

            roleCard.addEventListener('click', () => selectRole(role, roleCard));
            roleCard.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    selectRole(role, roleCard);
                }
            });

            roleGrid.appendChild(roleCard);
        });
    }

    function selectRole(role, cardElement) {
        // Clear previous selection
        document.querySelectorAll('.role-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Select new role
        cardElement.classList.add('selected');
        selectedRole = role;

        // Auto-advance to assessment after brief delay
        setTimeout(() => {
            currentStep = 2;
            currentQuestionIndex = 0;
            responses = [];
            generateSurveyQuestion();
            showSection(surveySection);
            updateProgress();
        }, 1000); // Slightly longer delay for role selection feedback
    }

    function generateRoleContext(role) {
        const context = roleContexts[role];
        if (!context) return;

        roleContext.innerHTML = `
            <h3>Assessment for ${role} Professionals</h3>
            <p>${context.context}</p>
            <div class="focus-areas">
                <h4>Key Focus Areas:</h4>
                <ul class="insight-list">
                    ${context.focusAreas.map(area => `<li>${area}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    function generateSurveyQuestion() {
        const questions = roleQuestions[selectedRole];
        if (!questions || currentQuestionIndex >= questions.length) return;

        const question = questions[currentQuestionIndex];
        
        surveyQuestions.innerHTML = `
            <div class="question-group">
                <div class="question-progress">
                    Question ${currentQuestionIndex + 1} of ${questions.length}
                </div>
                <h3>${question.question}</h3>
                <div class="options-container">
                    ${question.options.map((option, index) => `
                        <div class="option-item" data-score="${option.score}">
                            <input type="radio" id="option-${index}" name="question-${question.id}" value="${option.score}">
                            <label for="option-${index}" class="option-label">
                                ${option.text}
                            </label>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Add event listeners to options
        document.querySelectorAll('.option-item').forEach(item => {
            item.addEventListener('click', () => {
                const radio = item.querySelector('input[type="radio"]');
                radio.checked = true;
                selectOption(item);
            });
        });
    }

    function selectOption(selectedItem) {
        // Clear previous selections
        document.querySelectorAll('.option-item').forEach(item => {
            item.classList.remove('selected');
        });

        // Select current option
        selectedItem.classList.add('selected');

        // Auto-advance to next question after a brief delay
        setTimeout(() => {
            const selectedOption = document.querySelector('input[name^="question-"]:checked');
            if (selectedOption) {
                responses.push(parseInt(selectedOption.value));
                currentQuestionIndex++;
                
                const questions = roleQuestions[selectedRole];
                if (currentQuestionIndex < questions.length) {
                    generateSurveyQuestion();
                    updateProgress();
                } else {
                    // All questions completed, show submit button
                    showCompletionScreen();
                }
            }
        }, 800); // Small delay for user feedback
    }

    function updateProgress() {
        let progressPercentage;
        if (currentStep === 1) {
            progressPercentage = 20;
        } else if (currentStep === 2) {
            const questions = roleQuestions[selectedRole];
            const questionProgress = questions ? (currentQuestionIndex / questions.length) * 60 : 0;
            progressPercentage = 20 + questionProgress;
        } else {
            progressPercentage = 100;
        }

        progressFill.style.width = `${progressPercentage}%`;

        const stepTexts = [
            'Step 1 of 3: Select Role',
            `Step 2 of 3: Assessment Questions`,
            'Step 3 of 3: Results & Insights'
        ];

        progressText.textContent = stepTexts[currentStep - 1] || stepTexts[2];
    }

    function showSection(section) {
        // Hide all sections
        [roleSection, surveySection, resultsSection].forEach(s => {
            s.style.display = 'none';
        });

        // Show target section
        section.style.display = 'block';

        // Update navigation buttons
        updateNavigationButtons();
    }

    function updateNavigationButtons() {
        // Reset button visibility
        backBtn.style.display = 'none';
        continueBtn.style.display = 'none';
        submitBtn.style.display = 'none';

        if (currentStep === 1) {
            // No buttons needed - role selection auto-advances
        } else if (currentStep === 2) {
            // Always show back button during questions
            backBtn.style.display = 'block';
            backBtn.textContent = currentQuestionIndex > 0 ? 'Previous Question' : 'Back to Role';
        } else if (currentStep === 3) {
            // Results section - no navigation buttons needed
        }
    }

    function showCompletionScreen() {
        surveyQuestions.innerHTML = `
            <div class="completion-screen">
                <div class="completion-icon">✅</div>
                <h3>Assessment Complete!</h3>
                <p>You've answered all ${roleQuestions[selectedRole].length} questions. Ready to see your results?</p>
                <div class="completion-actions">
                    <button id="review-btn" class="secondary-btn">Review Answers</button>
                    <button id="complete-btn" class="primary-btn">View Results</button>
                </div>
            </div>
        `;

        // Add event listeners for completion actions
        document.getElementById('review-btn').addEventListener('click', () => {
            currentQuestionIndex = roleQuestions[selectedRole].length - 1;
            responses.pop(); // Remove the last response to allow re-answering
            generateSurveyQuestion();
            updateProgress();
        });

        document.getElementById('complete-btn').addEventListener('click', completeAssessment);
        
        updateNavigationButtons();
    }

    function goNext() {
        // No longer needed since role selection and questions both auto-advance
    }

    function goBack() {
        if (currentStep === 2) {
            if (currentQuestionIndex > 0) {
                currentQuestionIndex--;
                responses.pop();
                generateSurveyQuestion();
                updateProgress();
            } else {
                currentStep = 1;
                responses = [];
                showSection(roleSection);
                updateProgress();
            }
        }
    }

    function completeAssessment() {
        if (!selectedRole || responses.length === 0) {
            showError('Please complete all required fields.');
            return;
        }

        currentStep = 3;
        generateResults();
        showSection(resultsSection);
        updateProgress();
        assessmentComplete = true;
    }

    function generateResults() {
        const totalScore = responses.reduce((sum, score) => sum + score, 0);
        const maxPossibleScore = roleQuestions[selectedRole].length * 4;
        const percentageScore = Math.round((totalScore / maxPossibleScore) * 100);

        // Determine competency level
        let competencyLevel;
        for (const [level, data] of Object.entries(competencyLevels)) {
            if (percentageScore >= data.range[0] && percentageScore <= data.range[1]) {
                competencyLevel = data;
                break;
            }
        }

        resultDiv.innerHTML = `
            <div class="result-title">Assessment Complete!</div>
            <div class="result-level" style="color: ${competencyLevel.color}">${competencyLevel.title}</div>
            <div class="result-score">Score: ${percentageScore}% (${totalScore}/${maxPossibleScore} points)</div>
            <div class="result-description">
                ${competencyLevel.description}
            </div>
            
            <div class="result-insights">
                <h4>Recommended Next Steps</h4>
                <ul class="insight-list">
                    ${competencyLevel.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    function resetAssessment() {
        currentStep = 1;
        selectedRole = null;
        currentQuestionIndex = 0;
        responses = [];
        assessmentComplete = false;
        
        // Clear selections
        document.querySelectorAll('.role-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Reset to first section
        showSection(roleSection);
        updateProgress();
    }

    function shareResults() {
        if (!assessmentComplete) return;

        const totalScore = responses.reduce((sum, score) => sum + score, 0);
        const maxPossibleScore = roleQuestions[selectedRole].length * 4;
        const percentageScore = Math.round((totalScore / maxPossibleScore) * 100);

        let competencyLevel;
        for (const [level, data] of Object.entries(competencyLevels)) {
            if (percentageScore >= data.range[0] && percentageScore <= data.range[1]) {
                competencyLevel = data.title;
                break;
            }
        }

        const shareText = `I just completed an AI Competency Assessment! My level in ${selectedRole} is: ${competencyLevel} (${percentageScore}%).

Ready to assess your AI skills? Take the assessment: ${window.location.href}`;

        if (navigator.share) {
            navigator.share({
                title: 'AI Competency Assessment Results',
                text: shareText,
                url: window.location.href
            });
        } else {
            navigator.clipboard.writeText(shareText).then(() => {
                alert('Results copied to clipboard!');
            }).catch(() => {
                prompt('Copy this text to share your results:', shareText);
            });
        }
    }

    function showError(message) {
        document.querySelectorAll('.error-message').forEach(el => el.remove());

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        const activeSection = document.querySelector('.section[style*="block"]') || roleSection;
        activeSection.insertBefore(errorDiv, activeSection.firstChild);

        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Keyboard navigation support
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft' && backBtn.style.display !== 'none') {
            goBack();
        } else if (e.key === 'ArrowRight' && (continueBtn.style.display !== 'none' || submitBtn.style.display !== 'none')) {
            if (continueBtn.style.display !== 'none') {
                goNext();
            } else {
                completeAssessment();
            }
        }
    });

    // Initialize with role selection
    showSection(roleSection);
});