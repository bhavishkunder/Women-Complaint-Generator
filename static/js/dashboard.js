document.addEventListener('DOMContentLoaded', () => {
    const complaintForm = document.getElementById('complaint-form');
    const voiceInputBtn = document.getElementById('voice-input-btn');
    const stopRecordingBtn = document.getElementById('stop-recording-btn');
    const recordingIndicator = document.getElementById('recording-indicator');
    const recordingTime = document.getElementById('recording-time');
    const descriptionTextarea = document.querySelector('textarea[name="description"]');
    const complaintResult = document.getElementById('complaint-result');

    let recognition;
    let recordingStartTime;
    let recordingTimer;
    let originalDescription = '';

    // Auto-resize textarea
    function autoResizeTextarea() {
        descriptionTextarea.style.height = 'auto';
        descriptionTextarea.style.height = descriptionTextarea.scrollHeight + 'px';
    }

    descriptionTextarea.addEventListener('input', autoResizeTextarea);

    // Form submission
    complaintForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validate form data
        const description = descriptionTextarea.value.trim();
        if (!description) {
            showNotification('Please enter a description of the incident.', 'error');
            return;
        }

        // Store original description
        originalDescription = description;

        // Create FormData object
        const formData = new FormData();
        formData.append('description', description);

        try {
            const response = await fetch('/process_incident', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'incomplete') {
                // Show modal to collect missing information
                showMissingInfoModal(data.missing_info, data.current_details);
            } else if (data.structured_complaint) {
                displayComplaintResult(data.structured_complaint);
                complaintForm.reset();
                descriptionTextarea.style.height = 'auto';
                showNotification('Complaint submitted successfully', 'success');
            } else {
                throw new Error('No complaint data received');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('An error occurred while processing the complaint. Please try again.', 'error');
        }
    });

    function showMissingInfoModal(missingInfo, currentDetails) {
        // Create modal HTML
        const modalHTML = `
            <div class="modal-overlay">
                <div class="modal-content">
                    <h2>Additional Information Needed</h2>
                    <p>Please provide the following details to complete your complaint:</p>
                    <form id="missing-info-form" class="space-y-4">
                        ${missingInfo.date ? `
                            <div class="form-group">
                                <label for="incident-date">Date of Incident</label>
                                <input type="date" id="incident-date" name="date" required>
                            </div>
                        ` : ''}
                        ${missingInfo.time ? `
                            <div class="form-group">
                                <label for="incident-time">Time of Incident</label>
                                <input type="time" id="incident-time" name="time" required>
                            </div>
                        ` : ''}
                        ${missingInfo.place ? `
                            <div class="form-group">
                                <label for="incident-place">Place of Incident</label>
                                <input type="text" id="incident-place" name="place" required>
                            </div>
                        ` : ''}
                        <div class="button-group">
                            <button type="submit" class="submit-button">Submit</button>
                            <button type="button" class="cancel-button" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Handle form submission
        const missingInfoForm = document.getElementById('missing-info-form');
        missingInfoForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(missingInfoForm);
            formData.append('original_description', originalDescription);
            
            try {
                const response = await fetch('/update_incident', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.structured_complaint) {
                    displayComplaintResult(data.structured_complaint);
                    complaintForm.reset();
                    descriptionTextarea.style.height = 'auto';
                    showNotification('Complaint submitted successfully', 'success');
                    document.querySelector('.modal-overlay').remove();
                } else {
                    throw new Error('No complaint data received');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('An error occurred while updating the complaint. Please try again.', 'error');
            }
        });
    }

    // Voice recording
    if (voiceInputBtn) {
        voiceInputBtn.addEventListener('click', startRecording);
    }
    if (stopRecordingBtn) {
        stopRecordingBtn.addEventListener('click', stopRecording);
    }

    function startRecording() {
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = () => {
                voiceInputBtn.classList.add('hidden');
                recordingIndicator.classList.remove('hidden');
                recordingStartTime = Date.now();
                updateRecordingTime();
                showNotification('Recording started', 'success');
            };

            recognition.onresult = (event) => {
                let interimTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        descriptionTextarea.value += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }
                autoResizeTextarea();
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                showNotification('Error in speech recognition', 'error');
                stopRecording();
            };

            recognition.start();
        } else {
            showNotification('Speech recognition is not supported in your browser.', 'error');
        }
    }

    function stopRecording() {
        if (recognition) {
            recognition.stop();
            voiceInputBtn.classList.remove('hidden');
            recordingIndicator.classList.add('hidden');
            clearInterval(recordingTimer);
            showNotification('Recording stopped', 'success');
        }
    }

    function updateRecordingTime() {
        recordingTimer = setInterval(() => {
            const elapsedTime = Date.now() - recordingStartTime;
            const minutes = Math.floor(elapsedTime / 60000);
            const seconds = Math.floor((elapsedTime % 60000) / 1000);
            recordingTime.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    function displayComplaintResult(complaintText) {
        // Parse the complaint text into sections
        const sections = complaintText.split('\n\n').filter(Boolean);
        
        // Create the result HTML
        let resultHTML = `
            <div class="result-header">
                <h2>Complaint Analysis</h2>
                <button class="close-button" id="close-result">×</button>
            </div>
            <div class="result-content">
        `;

        let currentSection = '';
        sections.forEach(section => {
            if (section.includes('=========')) {
                // Section header
                currentSection = section.replace(/=/g, '').trim();
                resultHTML += `
                    <div class="result-section">
                        <h3 class="result-section-title">${currentSection}</h3>
                `;
            } else {
                // Section content
                const lines = section.split('\n');
                lines.forEach(line => {
                    if (line.includes(':')) {
                        const [label, value] = line.split(':').map(str => str.trim());
                        resultHTML += `
                            <div class="result-field">
                                <span class="result-label">${label}</span>
                                <span class="result-value">${value || ''}</span>
                            </div>
                        `;
                    } else if (line.trim()) {
                        resultHTML += `<p class="result-value mb-2">${line}</p>`;
                    }
                });
                resultHTML += `</div>`;
            }
        });

        resultHTML += `</div>`;

        // Update the complaint result container
        complaintResult.innerHTML = resultHTML;
        complaintResult.classList.remove('hidden');

        // Add close button functionality
        document.getElementById('close-result').addEventListener('click', () => {
            complaintResult.classList.add('hidden');
        });
    }

    // Notifications
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
});

