// Timetable Module

// Initialize timetable
function initializeTimetable() {
    const timetableContainer = document.getElementById('timetableContainer');
    if (!timetableContainer) return;

    // Check user role
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    const canEdit = ['admin', 'hod'].includes(userData.role);

    timetableContainer.innerHTML = `
        <div class="timetable-header">
            <h2>Class Schedule</h2>
            ${canEdit ? `
                <button onclick="showScheduleForm()" class="primary-button">
                    <i class="material-icons">add</i>
                    Add Schedule
                </button>
            ` : ''}
        </div>
        <div class="calendar-view">
            <div class="calendar-header">
                <button onclick="previousWeek()" class="icon-button">
                    <i class="material-icons">chevron_left</i>
                </button>
                <h3 id="weekDisplay"></h3>
                <button onclick="nextWeek()" class="icon-button">
                    <i class="material-icons">chevron_right</i>
                </button>
            </div>
            <div class="calendar-grid">
                <div class="time-column">
                    <div class="time-header">Time</div>
                    <div class="time-slots"></div>
                </div>
                <div class="days-grid" id="daysGrid"></div>
            </div>
        </div>
    `;

    // Initialize calendar
    initializeCalendar();
    loadSchedule();
}

// Initialize calendar view
function initializeCalendar() {
    // Generate time slots
    const timeSlots = document.querySelector('.time-slots');
    const startHour = 9; // 9 AM
    const endHour = 17; // 5 PM

    for (let hour = startHour; hour <= endHour; hour++) {
        timeSlots.innerHTML += `
            <div class="time-slot">${hour}:00</div>
        `;
    }

    // Generate days grid
    const daysGrid = document.getElementById('daysGrid');
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

    days.forEach(day => {
        daysGrid.innerHTML += `
            <div class="day-column">
                <div class="day-header">${day}</div>
                <div class="day-slots" data-day="${day}"></div>
            </div>
        `;
    });

    // Set current week
    updateWeekDisplay();
}

// Update week display
function updateWeekDisplay() {
    const weekDisplay = document.getElementById('weekDisplay');
    const currentDate = new Date();
    const startOfWeek = new Date(currentDate.setDate(currentDate.getDate() - currentDate.getDay() + 1));
    const endOfWeek = new Date(currentDate.setDate(currentDate.getDate() + 5));

    weekDisplay.textContent = `${startOfWeek.toLocaleDateString()} - ${endOfWeek.toLocaleDateString()}`;
}

// Navigate to previous week
function previousWeek() {
    // Implement week navigation
    updateWeekDisplay();
    loadSchedule();
}

// Navigate to next week
function nextWeek() {
    // Implement week navigation
    updateWeekDisplay();
    loadSchedule();
}

// Show schedule form
function showScheduleForm() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Add Schedule</h2>
            <form id="scheduleForm">
                <div class="form-group">
                    <select id="scheduleType" required>
                        <option value="">Select Type</option>
                        <option value="class">Class</option>
                        <option value="exam">Exam</option>
                    </select>
                </div>
                <div class="form-group">
                    <select id="scheduleSubject" required>
                        <option value="">Select Subject</option>
                    </select>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <select id="scheduleDay" required>
                            <option value="">Select Day</option>
                            <option value="Monday">Monday</option>
                            <option value="Tuesday">Tuesday</option>
                            <option value="Wednesday">Wednesday</option>
                            <option value="Thursday">Thursday</option>
                            <option value="Friday">Friday</option>
                            <option value="Saturday">Saturday</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <input type="time" id="scheduleTime" required>
                    </div>
                </div>
                <div class="form-group">
                    <select id="scheduleDuration" required>
                        <option value="1">1 Hour</option>
                        <option value="2">2 Hours</option>
                        <option value="3">3 Hours</option>
                    </select>
                </div>
                <div class="form-group">
                    <select id="scheduleSection" required>
                        <option value="">Select Section</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" onclick="closeModal()" class="secondary-button">
                        Cancel
                    </button>
                    <button type="submit" class="primary-button">
                        Add Schedule
                    </button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);

    // Load subjects and sections
    loadSubjectsAndSections();

    // Handle form submission
    document.getElementById('scheduleForm').addEventListener('submit', handleScheduleSubmit);
}

// Load subjects and sections
async function loadSubjectsAndSections() {
    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        // Load subjects
        const subjectSelect = document.getElementById('scheduleSubject');
        userData.subjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject;
            option.textContent = subject;
            subjectSelect.appendChild(option);
        });

        // Load sections
        const sections = await db.collection('sections')
            .where('department', '==', userData.department)
            .get();

        const sectionSelect = document.getElementById('scheduleSection');
        sections.forEach(doc => {
            const section = doc.data();
            const option = document.createElement('option');
            option.value = doc.id;
            option.textContent = section.name;
            sectionSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading subjects and sections:', error);
        showToast('Error loading form data', 'error');
    }
}

// Handle schedule submission
async function handleScheduleSubmit(e) {
    e.preventDefault();
    showLoadingSpinner();

    try {
        const scheduleData = {
            type: document.getElementById('scheduleType').value,
            subject: document.getElementById('scheduleSubject').value,
            day: document.getElementById('scheduleDay').value,
            time: document.getElementById('scheduleTime').value,
            duration: parseInt(document.getElementById('scheduleDuration').value),
            section: document.getElementById('scheduleSection').value,
            createdBy: auth.currentUser.uid,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        };

        // Add schedule to Firestore
        await db.collection('schedule').add(scheduleData);

        showToast('Schedule added successfully', 'success');
        closeModal();
        loadSchedule();
    } catch (error) {
        console.error('Error adding schedule:', error);
        showToast('Error adding schedule', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Load schedule
async function loadSchedule() {
    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        // Clear existing schedule
        document.querySelectorAll('.day-slots').forEach(daySlot => {
            daySlot.innerHTML = '';
        });

        // Get schedule based on role
        let scheduleQuery = db.collection('schedule');
        
        if (userData.role === 'student') {
            scheduleQuery = scheduleQuery.where('section', '==', userData.section);
        } else if (userData.role === 'faculty') {
            scheduleQuery = scheduleQuery.where('subject', 'in', userData.subjects);
        }

        const schedule = await scheduleQuery.get();

        schedule.forEach(doc => {
            const scheduleItem = doc.data();
            const daySlots = document.querySelector(`[data-day="${scheduleItem.day}"]`);
            
            if (daySlots) {
                const scheduleElement = document.createElement('div');
                scheduleElement.className = `schedule-item ${scheduleItem.type}`;
                scheduleElement.style.height = `${scheduleItem.duration * 60}px`;
                scheduleElement.style.top = calculateTopPosition(scheduleItem.time);
                
                scheduleElement.innerHTML = `
                    <div class="schedule-content">
                        <h4>${scheduleItem.subject}</h4>
                        <p>${scheduleItem.time}</p>
                        ${scheduleItem.type === 'exam' ? '<span class="exam-badge">Exam</span>' : ''}
                    </div>
                `;

                daySlots.appendChild(scheduleElement);
            }
        });
    } catch (error) {
        console.error('Error loading schedule:', error);
        showToast('Error loading schedule', 'error');
    }
}

// Calculate top position for schedule item
function calculateTopPosition(time) {
    const [hours, minutes] = time.split(':').map(Number);
    const startHour = 9; // 9 AM
    const minutesSinceStart = (hours - startHour) * 60 + minutes;
    return `${minutesSinceStart}px`;
}

// Initialize module
document.addEventListener('DOMContentLoaded', () => {
    auth.onAuthStateChanged(user => {
        if (user) {
            initializeTimetable();
        }
    });
}); 