// Smart Health Companion - Main Application Logic
// Simulates LangGraph-like agent orchestration for senior health management

class HealthCompanionApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.healthData = [];
        this.medications = [];
        this.emergencyContacts = [];
        this.healthInsights = [];
        this.medicationTaken = new Set();
        this.charts = {};
        
        this.init();
    }

    async init() {
        await this.loadSampleData();
        this.setupNavigation();
        this.setupEventHandlers();
        this.renderCurrentPage();
        this.startHealthMonitoring();
        this.checkMedicationReminders();
    }

    async loadSampleData() {
        // Sample health data from the provided JSON
        this.healthData = [
            {
                timestamp: "2025-09-05 08:00",
                heart_rate: 72,
                blood_pressure_systolic: 120,
                blood_pressure_diastolic: 80,
                activity_level: "light",
                medication_taken: true,
                sleep_hours: 7.5,
                mood: "good"
            },
            {
                timestamp: "2025-09-05 12:00", 
                heart_rate: 78,
                blood_pressure_systolic: 125,
                blood_pressure_diastolic: 82,
                activity_level: "moderate",
                medication_taken: true,
                sleep_hours: 7.5,
                mood: "good"
            },
            {
                timestamp: "2025-09-05 18:00",
                heart_rate: 85,
                blood_pressure_systolic: 135,
                blood_pressure_diastolic: 88,
                activity_level: "light",
                medication_taken: false,
                sleep_hours: 7.5,
                mood: "tired"
            }
        ];

        this.medications = [
            {
                id: 'lisinopril-morning',
                name: "Lisinopril",
                dosage: "10mg",
                frequency: "Once daily",
                time: "08:00",
                purpose: "Blood pressure control",
                taken: true,
                takenTime: "08:15"
            },
            {
                id: 'metformin-morning',
                name: "Metformin", 
                dosage: "500mg",
                frequency: "Twice daily",
                time: "08:00",
                purpose: "Diabetes management",
                taken: true,
                takenTime: "08:15"
            },
            {
                id: 'metformin-evening',
                name: "Metformin", 
                dosage: "500mg",
                frequency: "Twice daily",
                time: "18:00",
                purpose: "Diabetes management",
                taken: false,
                takenTime: null
            }
        ];

        this.emergencyContacts = [
            {
                name: "Dr. Smith",
                phone: "(555) 123-4567",
                type: "Primary Care"
            },
            {
                name: "Sarah (Daughter)",
                phone: "(555) 987-6543", 
                type: "Family"
            },
            {
                name: "Emergency Services",
                phone: "911",
                type: "Emergency"
            }
        ];

        this.healthInsights = [
            {
                type: "medication_reminder",
                message: "Don't forget your evening Metformin dose at 6:00 PM",
                priority: "high",
                timestamp: "2025-09-05 17:45",
                icon: "⚠️"
            },
            {
                type: "vital_alert", 
                message: "Blood pressure slightly elevated this evening. Consider rest and check again in 30 minutes.",
                priority: "medium",
                timestamp: "2025-09-05 18:05",
                icon: "💓"
            },
            {
                type: "activity_suggestion",
                message: "Great job staying active today! A gentle evening walk might help with relaxation.",
                priority: "low",
                timestamp: "2025-09-05 19:00",
                icon: "🚶‍♂️"
            }
        ];
    }

    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const targetPage = btn.getAttribute('data-page');
                this.navigateToPage(targetPage);
            });
        });
    }

    navigateToPage(pageName) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        // Show target page
        const targetPage = document.getElementById(`${pageName}-page`);
        if (targetPage) {
            targetPage.classList.add('active');
        }

        // Update navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-page="${pageName}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }

        this.currentPage = pageName;
        
        // Render page content with a small delay to ensure DOM is ready
        setTimeout(() => {
            this.renderCurrentPage();
        }, 50);
    }

    renderCurrentPage() {
        switch (this.currentPage) {
            case 'dashboard':
                this.renderDashboard();
                break;
            case 'medications':
                this.renderMedications();
                break;
            case 'trends':
                this.renderTrends();
                break;
            case 'emergency':
                this.renderEmergency();
                break;
            case 'family':
                this.renderFamily();
                break;
            case 'settings':
                this.renderSettings();
                break;
        }
    }

    renderDashboard() {
        const currentData = this.healthData[this.healthData.length - 1];
        
        // Update heart rate
        const heartRateEl = document.getElementById('current-heart-rate');
        if (heartRateEl) {
            heartRateEl.textContent = currentData.heart_rate;
        }

        // Update blood pressure
        const bpEl = document.getElementById('current-bp');
        if (bpEl) {
            bpEl.textContent = `${currentData.blood_pressure_systolic}/${currentData.blood_pressure_diastolic}`;
        }

        // Update activity
        const activityEl = document.getElementById('current-activity');
        if (activityEl) {
            activityEl.textContent = currentData.activity_level.charAt(0).toUpperCase() + currentData.activity_level.slice(1);
        }

        // Update sleep
        const sleepEl = document.getElementById('current-sleep');
        if (sleepEl) {
            sleepEl.textContent = currentData.sleep_hours;
        }

        // Render health insights
        this.renderHealthInsights();
    }

    renderHealthInsights() {
        const insightsContainer = document.getElementById('health-insights');
        if (!insightsContainer) return;

        insightsContainer.innerHTML = '';
        
        this.healthInsights.forEach(insight => {
            const insightCard = document.createElement('div');
            insightCard.className = `insight-card ${insight.priority}-priority`;
            
            insightCard.innerHTML = `
                <div class="insight-icon">${insight.icon}</div>
                <div class="insight-content">
                    <p>${insight.message}</p>
                    <div class="insight-timestamp">${this.formatTime(insight.timestamp)}</div>
                </div>
            `;
            
            insightsContainer.appendChild(insightCard);
        });
    }

    renderMedications() {
        const medicationList = document.getElementById('medication-list');
        if (!medicationList) return;

        medicationList.innerHTML = '';
        
        this.medications.forEach(med => {
            const medItem = document.createElement('div');
            const status = med.taken ? 'taken' : (this.isMedicationOverdue(med) ? 'overdue' : 'pending');
            medItem.className = `medication-item ${status}`;
            
            const statusText = med.taken ? 'Taken' : (this.isMedicationOverdue(med) ? 'Overdue' : 'Pending');
            const statusClass = med.taken ? 'taken' : (this.isMedicationOverdue(med) ? 'overdue' : 'pending');
            
            medItem.innerHTML = `
                <div class="medication-info">
                    <h4>${med.name} ${med.dosage}</h4>
                    <p>Scheduled for ${med.time} - ${med.purpose}</p>
                    ${med.taken && med.takenTime ? `<p><small>Taken at ${med.takenTime}</small></p>` : ''}
                </div>
                <div class="medication-status">
                    <span class="status-badge ${statusClass}">${statusText}</span>
                    ${!med.taken ? `<button class="btn btn--primary" data-med-id="${med.id}">Mark Taken</button>` : ''}
                </div>
            `;
            
            // Add event listener for mark taken button
            const markBtn = medItem.querySelector(`[data-med-id="${med.id}"]`);
            if (markBtn) {
                markBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.markMedicationTaken(med.id);
                });
            }
            
            medicationList.appendChild(medItem);
        });

        // Render compliance chart
        setTimeout(() => {
            this.renderComplianceChart();
        }, 100);
    }

    renderComplianceChart() {
        const ctx = document.getElementById('compliance-chart');
        if (!ctx) return;

        if (this.charts.compliance) {
            this.charts.compliance.destroy();
        }

        // Generate mock compliance data for the week
        const weekData = [
            { day: 'Mon', compliance: 100 },
            { day: 'Tue', compliance: 100 },
            { day: 'Wed', compliance: 85 },
            { day: 'Thu', compliance: 100 },
            { day: 'Fri', compliance: 67 },
            { day: 'Sat', compliance: 100 },
            { day: 'Sun', compliance: 100 }
        ];

        this.charts.compliance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: weekData.map(d => d.day),
                datasets: [{
                    label: 'Medication Compliance (%)',
                    data: weekData.map(d => d.compliance),
                    backgroundColor: '#1FB8CD',
                    borderColor: '#1FB8CD',
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            font: { size: 16 }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            font: { size: 14 },
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    x: {
                        ticks: {
                            font: { size: 14 }
                        }
                    }
                }
            }
        });
    }

    renderTrends() {
        // Add small delay to ensure DOM is ready
        setTimeout(() => {
            this.renderBloodPressureChart();
            this.renderHeartRateChart();
        }, 100);
    }

    renderBloodPressureChart() {
        const ctx = document.getElementById('bp-chart');
        if (!ctx) return;

        if (this.charts.bloodPressure) {
            this.charts.bloodPressure.destroy();
        }

        const timestamps = this.healthData.map(d => this.formatTime(d.timestamp, true));
        const systolicData = this.healthData.map(d => d.blood_pressure_systolic);
        const diastolicData = this.healthData.map(d => d.blood_pressure_diastolic);

        this.charts.bloodPressure = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [
                    {
                        label: 'Systolic',
                        data: systolicData,
                        borderColor: '#B4413C',
                        backgroundColor: '#B4413C',
                        fill: false,
                        tension: 0.1,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    },
                    {
                        label: 'Diastolic',
                        data: diastolicData,
                        borderColor: '#1FB8CD',
                        backgroundColor: '#1FB8CD',
                        fill: false,
                        tension: 0.1,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            font: { size: 16 }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 60,
                        max: 160,
                        ticks: {
                            font: { size: 14 }
                        }
                    },
                    x: {
                        ticks: {
                            font: { size: 14 }
                        }
                    }
                }
            }
        });
    }

    renderHeartRateChart() {
        const ctx = document.getElementById('hr-chart');
        if (!ctx) return;

        if (this.charts.heartRate) {
            this.charts.heartRate.destroy();
        }

        const timestamps = this.healthData.map(d => this.formatTime(d.timestamp, true));
        const heartRateData = this.healthData.map(d => d.heart_rate);

        this.charts.heartRate = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Heart Rate (BPM)',
                    data: heartRateData,
                    borderColor: '#FFC185',
                    backgroundColor: '#FFC185',
                    fill: false,
                    tension: 0.1,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            font: { size: 16 }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 60,
                        max: 100,
                        ticks: {
                            font: { size: 14 }
                        }
                    },
                    x: {
                        ticks: {
                            font: { size: 14 }
                        }
                    }
                }
            }
        });
    }

    renderEmergency() {
        // Emergency contacts are already in the HTML, no dynamic rendering needed
        console.log('Emergency page rendered');
    }

    renderFamily() {
        // Family page content is mostly static, could add dynamic message loading here
        console.log('Family page rendered');
    }

    renderSettings() {
        const contactsList = document.getElementById('emergency-contacts-list');
        if (!contactsList) return;

        contactsList.innerHTML = '';
        
        this.emergencyContacts.forEach(contact => {
            const contactItem = document.createElement('div');
            contactItem.className = 'contact-item';
            
            contactItem.innerHTML = `
                <div class="contact-info">
                    <h4>${contact.name}</h4>
                    <p>${contact.phone} - ${contact.type}</p>
                </div>
                <button class="btn btn--outline btn--sm">Edit</button>
            `;
            
            // Add event listener for edit button
            const editBtn = contactItem.querySelector('.btn');
            editBtn.addEventListener('click', () => {
                this.editContact(contact.name);
            });
            
            contactsList.appendChild(contactItem);
        });
    }

    setupEventHandlers() {
        // Setup dashboard action buttons
        const emergencyBtn = document.querySelector('.emergency-btn');
        if (emergencyBtn) {
            emergencyBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showEmergencyDialog();
            });
        }

        const voiceBtn = document.querySelector('[onclick="openVoiceInterface()"]');
        if (voiceBtn) {
            voiceBtn.removeAttribute('onclick');
            voiceBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openVoiceInterface();
            });
        }

        const vitalsBtn = document.querySelector('[onclick="checkVitals()"]');
        if (vitalsBtn) {
            vitalsBtn.removeAttribute('onclick');
            vitalsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.checkVitals();
            });
        }

        const familyBtn = document.querySelector('[onclick="callFamily()"]');
        if (familyBtn) {
            familyBtn.removeAttribute('onclick');
            familyBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.callFamily();
            });
        }

        // Setup medication reminder button
        const medBtn = document.querySelector('[onclick*="metformin-evening"]');
        if (medBtn) {
            medBtn.removeAttribute('onclick');
            medBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.markMedicationTaken('metformin-evening');
            });
        }

        // Setup modal close buttons
        const voiceCloseBtn = document.querySelector('#voice-modal .modal-close');
        if (voiceCloseBtn) {
            voiceCloseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeVoiceModal();
            });
        }

        const emergencyCloseBtn = document.querySelector('[onclick="closeEmergencyModal()"]');
        if (emergencyCloseBtn) {
            emergencyCloseBtn.removeAttribute('onclick');
            emergencyCloseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeEmergencyModal();
            });
        }

        // Setup voice command processing
        const voiceProcessBtn = document.querySelector('[onclick="processVoiceCommand()"]');
        if (voiceProcessBtn) {
            voiceProcessBtn.removeAttribute('onclick');
            voiceProcessBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.processVoiceCommand();
            });
        }

        // Setup family share button
        const shareBtn = document.querySelector('[onclick="shareSummary()"]');
        if (shareBtn) {
            shareBtn.removeAttribute('onclick');
            shareBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.shareSummary();
            });
        }

        // Setup voice input enter key
        const voiceInput = document.getElementById('voice-input');
        if (voiceInput) {
            voiceInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.processVoiceCommand();
                }
            });
        }
    }

    markMedicationTaken(medicationId) {
        const medication = this.medications.find(med => med.id === medicationId);
        if (medication) {
            medication.taken = true;
            medication.takenTime = new Date().toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: false 
            });
            
            // Remove medication reminder from insights
            this.healthInsights = this.healthInsights.filter(insight => 
                !(insight.type === 'medication_reminder' && insight.message.includes(medication.name))
            );
            
            // Add positive feedback insight
            this.healthInsights.unshift({
                type: 'medication_taken',
                message: `Great! You've taken your ${medication.name}. Keep up the good medication compliance.`,
                priority: 'low',
                timestamp: new Date().toISOString().slice(0, 16).replace('T', ' '),
                icon: '✅'
            });

            // Update the display
            this.renderCurrentPage();
            
            // Show success message
            this.showNotification(`${medication.name} marked as taken!`, 'success');
        }
    }

    showEmergencyDialog() {
        const modal = document.getElementById('emergency-modal');
        if (modal) {
            modal.classList.remove('hidden');
            modal.style.display = 'flex';
        }
    }

    closeEmergencyModal() {
        const modal = document.getElementById('emergency-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.style.display = 'none';
        }
    }

    openVoiceInterface() {
        const modal = document.getElementById('voice-modal');
        if (modal) {
            modal.classList.remove('hidden');
            modal.style.display = 'flex';
            const input = document.getElementById('voice-input');
            if (input) {
                setTimeout(() => input.focus(), 100);
            }
        }
    }

    closeVoiceModal() {
        const modal = document.getElementById('voice-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.style.display = 'none';
        }
        
        const response = document.getElementById('voice-response');
        if (response) {
            response.innerHTML = '';
        }
        
        const input = document.getElementById('voice-input');
        if (input) {
            input.value = '';
        }
    }

    processVoiceCommand() {
        const input = document.getElementById('voice-input');
        const response = document.getElementById('voice-response');
        
        if (!input || !response) return;
        
        const command = input.value.toLowerCase().trim();
        if (!command) return;
        
        let responseText = '';
        
        // Agent-like decision making for voice commands (LangGraph-inspired)
        if (command.includes('medication') || command.includes('pills')) {
            responseText = this.handleMedicationQuery(command);
        } else if (command.includes('blood pressure') || command.includes('heart rate')) {
            responseText = this.handleVitalQuery(command);
        } else if (command.includes('how am i') || command.includes('health status')) {
            responseText = this.handleStatusQuery();
        } else if (command.includes('emergency') || command.includes('help')) {
            responseText = this.handleEmergencyQuery();
        } else if (command.includes('family') || command.includes('daughter')) {
            responseText = this.handleFamilyQuery();
        } else {
            responseText = "I can help you with your medications, health status, vitals, emergency contacts, or family communication. What would you like to know?";
        }
        
        response.innerHTML = `<p><strong>You asked:</strong> "${input.value}"</p><p><strong>Health Assistant:</strong> ${responseText}</p>`;
        input.value = '';
    }

    handleMedicationQuery(command) {
        const pendingMeds = this.medications.filter(med => !med.taken);
        const takenMeds = this.medications.filter(med => med.taken);
        
        if (command.includes('taken') || command.includes('completed')) {
            return `You've taken ${takenMeds.length} of ${this.medications.length} medications today. ${pendingMeds.length > 0 ? `You still need to take: ${pendingMeds.map(m => m.name).join(', ')}.` : 'All medications completed for today!'}`;
        } else if (command.includes('reminder') || command.includes('when')) {
            const nextMed = pendingMeds[0];
            return nextMed ? `Your next medication is ${nextMed.name} ${nextMed.dosage} scheduled for ${nextMed.time}.` : 'No pending medications for today.';
        } else {
            return `Today's medications: ${this.medications.map(m => `${m.name} at ${m.time} ${m.taken ? '(✅ taken)' : '(⏰ pending)'}`).join(', ')}.`;
        }
    }

    handleVitalQuery(command) {
        const currentData = this.healthData[this.healthData.length - 1];
        
        if (command.includes('blood pressure')) {
            return `Your current blood pressure is ${currentData.blood_pressure_systolic}/${currentData.blood_pressure_diastolic} mmHg. This is slightly elevated from your normal range. Consider resting and checking again in 30 minutes.`;
        } else if (command.includes('heart rate')) {
            return `Your current heart rate is ${currentData.heart_rate} bpm. This is within normal range but slightly elevated from this morning.`;
        } else {
            return `Current vitals: Heart rate ${currentData.heart_rate} bpm, Blood pressure ${currentData.blood_pressure_systolic}/${currentData.blood_pressure_diastolic} mmHg. Overall status: monitoring blood pressure elevation.`;
        }
    }

    handleStatusQuery() {
        const currentData = this.healthData[this.healthData.length - 1];
        const takenMeds = this.medications.filter(med => med.taken).length;
        const totalMeds = this.medications.length;
        
        return `Overall health status: Good with monitoring needed. You've had ${currentData.sleep_hours} hours of sleep, taken ${takenMeds} of ${totalMeds} medications today, and maintained ${currentData.activity_level} activity. Your blood pressure is slightly elevated this evening, so please continue monitoring.`;
    }

    handleEmergencyQuery() {
        return `Your emergency contacts are: Dr. Smith at (555) 123-4567, your daughter Sarah at (555) 987-6543, and Emergency Services at 911. In case of emergency, call 911 first, then notify your doctor and family.`;
    }

    handleFamilyQuery() {
        return `Your daughter Sarah sent a message today reminding you about your evening medication. You can share your daily health summary with her from the Family page. Would you like me to help you send her an update?`;
    }

    checkVitals() {
        // Simulate taking new vitals
        const newReading = {
            timestamp: new Date().toISOString().slice(0, 16).replace('T', ' '),
            heart_rate: Math.floor(Math.random() * 10) + 75,
            blood_pressure_systolic: Math.floor(Math.random() * 15) + 125,
            blood_pressure_diastolic: Math.floor(Math.random() * 8) + 80,
            activity_level: "light",
            medication_taken: false,
            sleep_hours: 7.5,
            mood: "good"
        };
        
        this.healthData.push(newReading);
        
        // Generate insight based on new reading
        if (newReading.blood_pressure_systolic > 130) {
            this.healthInsights.unshift({
                type: 'vital_alert',
                message: `New reading shows blood pressure at ${newReading.blood_pressure_systolic}/${newReading.blood_pressure_diastolic}. Continue monitoring and consider contacting your doctor.`,
                priority: 'medium',
                timestamp: newReading.timestamp,
                icon: '💓'
            });
        }
        
        this.renderCurrentPage();
        this.showNotification('New vitals recorded!', 'success');
    }

    callFamily() {
        // Simulate calling family - would open phone dialer in real app
        this.showNotification('Calling Sarah...', 'info');
        setTimeout(() => {
            this.showNotification('Call connected to Sarah', 'success');
        }, 2000);
    }

    shareSummary() {
        // Simulate sharing health summary with family
        this.showNotification('Daily health summary shared with family', 'success');
        
        // Add to family messages
        const messageList = document.querySelector('.message-list');
        if (messageList) {
            const newMessage = document.createElement('div');
            newMessage.className = 'message-item';
            newMessage.innerHTML = `
                <div class="message-sender">You</div>
                <div class="message-content">Daily health update: Overall doing well, took morning medications, blood pressure slightly elevated this evening.</div>
                <div class="message-time">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
            `;
            messageList.appendChild(newMessage);
        }
    }

    editContact(contactName) {
        this.showNotification(`Edit contact feature would open for ${contactName}`, 'info');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--color-${type === 'success' ? 'success' : type === 'error' ? 'error' : 'info'});
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            z-index: 1001;
            box-shadow: var(--shadow-lg);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    startHealthMonitoring() {
        // Simulate periodic health monitoring (agent-like behavior)
        setInterval(() => {
            this.runHealthAgent();
        }, 300000); // Run every 5 minutes
    }

    runHealthAgent() {
        // LangGraph-inspired agent decision making
        const currentTime = new Date();
        const currentHour = currentTime.getHours();
        
        // Check for medication reminders
        this.checkMedicationReminders();
        
        // Check for vital sign patterns
        this.analyzeVitalTrends();
        
        // Generate time-based insights
        this.generateTimeBasedInsights(currentHour);
    }

    checkMedicationReminders() {
        const currentTime = new Date();
        const currentTimeString = currentTime.toTimeString().slice(0, 5);
        
        this.medications.forEach(med => {
            if (!med.taken && med.time <= currentTimeString) {
                const existingReminder = this.healthInsights.find(insight => 
                    insight.type === 'medication_reminder' && insight.message.includes(med.name)
                );
                
                if (!existingReminder) {
                    this.healthInsights.unshift({
                        type: 'medication_reminder',
                        message: `Time to take your ${med.name} ${med.dosage}!`,
                        priority: 'high',
                        timestamp: new Date().toISOString().slice(0, 16).replace('T', ' '),
                        icon: '💊'
                    });
                }
            }
        });
    }

    analyzeVitalTrends() {
        if (this.healthData.length < 2) return;
        
        const recent = this.healthData.slice(-2);
        const bpIncrease = recent[1].blood_pressure_systolic - recent[0].blood_pressure_systolic;
        const hrIncrease = recent[1].heart_rate - recent[0].heart_rate;
        
        if (bpIncrease > 10) {
            this.healthInsights.unshift({
                type: 'trend_alert',
                message: `Blood pressure has increased by ${bpIncrease} points. Consider rest and monitoring.`,
                priority: 'medium',
                timestamp: new Date().toISOString().slice(0, 16).replace('T', ' '),
                icon: '📈'
            });
        }
        
        if (hrIncrease > 15) {
            this.healthInsights.unshift({
                type: 'trend_alert',
                message: `Heart rate has increased significantly. Take a moment to rest.`,
                priority: 'medium',
                timestamp: new Date().toISOString().slice(0, 16).replace('T', ' '),
                icon: '💓'
            });
        }
    }

    generateTimeBasedInsights(currentHour) {
        // Morning insights
        if (currentHour >= 7 && currentHour <= 9) {
            const morningMeds = this.medications.filter(med => med.time.startsWith('08') && !med.taken);
            if (morningMeds.length > 0) {
                this.addInsightIfNotExists('morning_routine', 'Good morning! Don\'t forget to take your morning medications with breakfast.', 'medium', '🌅');
            }
        }
        
        // Evening insights
        if (currentHour >= 17 && currentHour <= 19) {
            const eveningMeds = this.medications.filter(med => med.time.startsWith('18') && !med.taken);
            if (eveningMeds.length > 0) {
                this.addInsightIfNotExists('evening_routine', 'Evening medication reminder: Time for your evening doses.', 'high', '🌆');
            }
        }
        
        // Bedtime insights
        if (currentHour >= 21) {
            this.addInsightIfNotExists('bedtime_routine', 'Getting close to bedtime. Consider winding down for good sleep quality.', 'low', '😴');
        }
    }

    addInsightIfNotExists(type, message, priority, icon) {
        const exists = this.healthInsights.find(insight => insight.type === type);
        if (!exists) {
            this.healthInsights.unshift({
                type: type,
                message: message,
                priority: priority,
                timestamp: new Date().toISOString().slice(0, 16).replace('T', ' '),
                icon: icon
            });
            
            // Limit insights to prevent overflow
            if (this.healthInsights.length > 10) {
                this.healthInsights = this.healthInsights.slice(0, 10);
            }
        }
    }

    isMedicationOverdue(medication) {
        const currentTime = new Date();
        const medTime = new Date();
        const [hours, minutes] = medication.time.split(':');
        medTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);
        
        return !medication.taken && currentTime > medTime;
    }

    formatTime(timestamp, shortFormat = false) {
        const date = new Date(timestamp);
        if (shortFormat) {
            return date.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: false 
            });
        }
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new HealthCompanionApp();
});

// Handle modal closing on outside click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.add('hidden');
        e.target.style.display = 'none';
    }
});

// Handle keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        // Close any open modals
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
            modal.style.display = 'none';
        });
    }
});