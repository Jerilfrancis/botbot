const api = (path, options = {}) => fetch(`/api${path}`, {
  headers: { 'Content-Type': 'application/json' },
  ...options
}).then(r => r.json());

async function renderCourses() {
  const container = document.getElementById('course-list');
  if (!container) return;
  const courses = await api('/courses');
  container.innerHTML = courses.map(course => `
    <article class="card">
      <h3>${course.title}</h3>
      <p>${course.topic}</p>
      <p>Mentor: ${course.mentor_name}</p>
      <a href="/course/${course.id}">Open Course</a>
    </article>
  `).join('') || '<p>No courses yet. Add data via API.</p>';
}

function setupTheme() {
  const btn = document.getElementById('theme-toggle');
  if (!btn) return;
  const saved = localStorage.getItem('learnx-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  btn.onclick = () => {
    const next = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('learnx-theme', next);
  };
}

async function requestSummary() {
  const out = document.getElementById('summary-output');
  const data = await api('/ai/summary', {
    method: 'POST',
    body: JSON.stringify({ content: 'This module explains JavaScript fundamentals, functions, arrays, DOM, and asynchronous patterns used in projects.' })
  });
  if (out) out.textContent = data.summary;
}

async function loadAdminAnalytics() {
  const out = document.getElementById('admin-output');
  const data = await api('/admin/analytics');
  if (out) out.textContent = JSON.stringify(data, null, 2);
}

async function loadMentorAnalytics(id) {
  const out = document.getElementById('mentor-output');
  const data = await api(`/mentor/${id}/analytics`);
  if (out) out.textContent = JSON.stringify(data, null, 2);
}

window.requestSummary = requestSummary;
window.loadAdminAnalytics = loadAdminAnalytics;
window.loadMentorAnalytics = loadMentorAnalytics;

setupTheme();
renderCourses();
