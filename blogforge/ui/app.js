// BlogForge Studio SPA Frontend Logic
let currentPost = null;
let lintDebounceTimer = null;
let activeSidebarTab = 'posts';

document.addEventListener('DOMContentLoaded', () => {
  loadStatus();
  loadPosts();
  setInterval(loadStatus, 30000); // Poll status every 30s
});

async function api(path, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch('/api/' + path.replace(/^\//, ''), opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || 'API Error');
  }
  return await res.json();
}

function switchSidebarTab(tab) {
  activeSidebarTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.list-container').forEach(c => c.style.display = 'none');

  if (tab === 'posts') {
    document.querySelectorAll('.tab-btn')[0].classList.add('active');
    document.getElementById('tabPosts').style.display = 'block';
  } else if (tab === 'topics') {
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
    document.getElementById('tabTopics').style.display = 'block';
    loadTopics();
  } else if (tab === 'schedule') {
    document.querySelectorAll('.tab-btn')[2].classList.add('active');
    document.getElementById('tabSchedule').style.display = 'block';
    loadSchedule();
  }
}

async function loadStatus() {
  try {
    const data = await api('/status');
    const branchEl = document.getElementById('gitBranch');
    const dirty = (data.git.changed || []).length > 0;
    branchEl.innerHTML = `Git: <strong>${data.git.branch}</strong> ${dirty ? '<span style="color:var(--amber)">● edited</span>' : '<span style="color:var(--green)">✓ clean</span>'}`;
    
    const schedBtn = document.getElementById('toggleSchedBtn');
    if (data.scheduler.enabled) {
      schedBtn.innerText = 'Daemon: Active';
      schedBtn.style.color = 'var(--green)';
    } else {
      schedBtn.innerText = 'Daemon: Off';
      schedBtn.style.color = 'var(--text-muted)';
    }
  } catch (err) {
    console.error('loadStatus error:', err);
  }
}

async function loadPosts() {
  const listEl = document.getElementById('postsList');
  listEl.innerHTML = '<div style="color:var(--text-muted); padding:10px;">Loading posts...</div>';
  try {
    const data = await api('/posts');
    document.getElementById('postCount').innerText = data.posts.length;
    if (data.posts.length === 0) {
      listEl.innerHTML = '<div style="padding:10px;">No posts found.</div>';
      return;
    }
    listEl.innerHTML = data.posts.map(p => `
      <div class="post-item ${currentPost && currentPost.path === p.path ? 'active' : ''}" onclick="selectPost('${p.path}')">
        <div class="post-title">${escapeHtml(p.title || p.path)}</div>
        <div class="post-meta">
          <span>${p.date || 'no date'}</span>
          <span>•</span>
          <span>${p.section}</span>
          ${p.draft ? '<span class="badge badge-draft">Draft</span>' : '<span class="badge badge-published">Published</span>'}
          ${p.reviewed ? '<span class="badge badge-reviewed">Reviewed</span>' : ''}
        </div>
      </div>
    `).join('');
  } catch (err) {
    listEl.innerHTML = `<div style="color:var(--red); padding:10px;">Failed to load posts: ${err.message}</div>`;
  }
}

async function selectPost(relPath) {
  try {
    const post = await api(`/post?path=${encodeURIComponent(relPath)}`);
    currentPost = post;
    document.getElementById('currentPostPath').innerText = post.path;
    document.getElementById('postEditor').value = post.content;
    document.getElementById('saveBtn').disabled = false;
    document.getElementById('reviewBtn').disabled = false;
    document.getElementById('publishBtn').disabled = false;

    const isReviewed = post.metadata.reviewed === true;
    const reviewBtn = document.getElementById('reviewBtn');
    reviewBtn.innerText = isReviewed ? 'Reviewed ✓' : 'Approve (Reviewed)';
    reviewBtn.classList.toggle('btn-primary', isReviewed);

    updateLintDisplay(post.linter);
    loadPosts(); // refresh active highlights
  } catch (err) {
    alert('Failed to load post: ' + err.message);
  }
}

function onEditorChange() {
  clearTimeout(lintDebounceTimer);
  lintDebounceTimer = setTimeout(async () => {
    const content = document.getElementById('postEditor').value;
    const section = currentPost && currentPost.metadata.section ? currentPost.metadata.section : 'sysadmin';
    try {
      const report = await api('/lint', 'POST', { content, section });
      updateLintDisplay(report);
    } catch (err) {
      console.error('live lint failed:', err);
    }
  }, 400);
}

function updateLintDisplay(report) {
  if (!report) return;
  const scoreEl = document.getElementById('lintScore');
  const verdictEl = document.getElementById('lintVerdict');
  const findingsEl = document.getElementById('lintFindings');

  const score = report.score;
  scoreEl.innerText = score + '/100';
  scoreEl.className = 'score-val ' + (score >= 80 ? 'score-high' : score >= 60 ? 'score-med' : 'score-low');
  verdictEl.innerText = `${report.words} words • ${report.fails} fails, ${report.warnings} warnings`;

  if (!report.findings || report.findings.length === 0) {
    findingsEl.innerHTML = '<p style="color:var(--green); font-size:0.85rem;">✓ Perfect match to house style bounds!</p>';
    return;
  }

  findingsEl.innerHTML = report.findings.map(f => `
    <div class="finding-item ${f.severity === 'fail' ? 'finding-fail' : 'finding-warn'}">
      <div class="finding-title">${f.severity === 'fail' ? '❌' : '⚠️'} ${escapeHtml(f.message)}</div>
      ${f.fix ? `<div class="finding-fix">💡 ${escapeHtml(f.fix)}</div>` : ''}
    </div>
  `).join('');
}

async function saveCurrentPost() {
  if (!currentPost) return;
  const content = document.getElementById('postEditor').value;
  try {
    const res = await api('/post/save', 'POST', { path: currentPost.path, content });
    if (res.linter) updateLintDisplay(res.linter);
    loadStatus();
    alert('Saved successfully!');
  } catch (err) {
    alert('Save failed: ' + err.message);
  }
}

async function toggleReviewCurrentPost() {
  if (!currentPost) return;
  const isReviewed = currentPost.metadata.reviewed === true;
  try {
    await api('/post/review', 'POST', { path: currentPost.path, unapprove: isReviewed });
    await selectPost(currentPost.path);
  } catch (err) {
    alert('Review toggle failed: ' + err.message);
  }
}

async function publishCurrentPost() {
  if (!currentPost) return;
  if (!confirm(`Publish ${currentPost.path} now? (Flips draft: false and updates date)`)) return;
  try {
    const res = await api('/post/publish', 'POST', { path: currentPost.path });
    alert(res.message);
    await selectPost(currentPost.path);
    loadStatus();
  } catch (err) {
    alert('Publish failed: ' + err.message);
  }
}

// Modals helpers
function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

function openGenerateModal() { openModal('generateModal'); }

async function runGenerate() {
  const btn = document.getElementById('startGenBtn');
  btn.disabled = true;
  btn.innerText = 'Drafting...';
  try {
    const res = await api('/generate', 'POST', {
      title: document.getElementById('genTitle').value,
      section: document.getElementById('genSection').value,
      provider: document.getElementById('genProvider').value,
      tags: document.getElementById('genTags').value,
      facts: document.getElementById('genFacts').value,
    });
    closeModal('generateModal');
    await loadPosts();
    if (res.path) {
      await selectPost(res.path);
    }
  } catch (err) {
    alert('Generation error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerText = 'Start Drafting';
  }
}

async function openGitModal() {
  openModal('gitModal');
  const diffEl = document.getElementById('gitDiffFiles');
  diffEl.innerText = 'Checking git status...';
  try {
    const status = await api('/git/status');
    if (status.changed.length === 0) {
      diffEl.innerText = 'Working tree clean. Nothing to commit.';
    } else {
      diffEl.innerText = status.changed.map(c => `${c.status} ${c.path}`).join('\n');
    }
  } catch (err) {
    diffEl.innerText = 'Failed to load git status: ' + err.message;
  }
}

async function commitChanges() {
  const msg = document.getElementById('gitCommitMsg').value;
  try {
    const res = await api('/git/commit', 'POST', { message: msg });
    alert(res.ok ? 'Committed!' : 'Commit failed: ' + res.error);
    await openGitModal();
    loadStatus();
  } catch (err) {
    alert('Commit error: ' + err.message);
  }
}

async function commitAndPush() {
  const btn = document.getElementById('gitPushBtn');
  btn.disabled = true;
  btn.innerText = 'Pushing...';
  const msg = document.getElementById('gitCommitMsg').value;
  try {
    const cRes = await api('/git/commit', 'POST', { message: msg });
    const pRes = await api('/git/push', 'POST', {});
    if (pRes.ok) {
      alert('Committed and pushed successfully to GitHub/remote!');
      closeModal('gitModal');
      loadStatus();
    } else {
      alert('Push failed: ' + pRes.error);
    }
  } catch (err) {
    alert('Git push error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerText = 'Commit & Push';
  }
}

// Topics Tab
async function loadTopics() {
  const listEl = document.getElementById('topicsList');
  listEl.innerHTML = '<div style="color:var(--text-muted); padding:10px;">Finding backlog & gaps...</div>';
  try {
    const data = await api('/topics');
    if (data.topics.length === 0) {
      listEl.innerHTML = '<div style="padding:10px;">No topics in catalog.</div>';
      return;
    }
    listEl.innerHTML = data.topics.map(t => `
      <div class="post-item" onclick="draftTopic('${escapeHtml(t.title)}', '${t.section || 'sysadmin'}', '${t.id || ''}')">
        <div class="post-title">${escapeHtml(t.title)}</div>
        <div class="post-meta">
          <span>${t.section || 'sysadmin'}</span>
          <span>•</span>
          <span style="color:var(--accent);">Score: ${t.score}</span>
        </div>
      </div>
    `).join('');
  } catch (err) {
    listEl.innerHTML = `<div style="color:var(--red); padding:10px;">Error: ${err.message}</div>`;
  }
}

function draftTopic(title, section, id) {
  openGenerateModal();
  document.getElementById('genTitle').value = title;
  document.getElementById('genSection').value = section;
}

// Schedule Tab
async function loadSchedule() {
  const listEl = document.getElementById('scheduleList');
  listEl.innerHTML = '<div style="color:var(--text-muted); padding:10px;">Loading schedule...</div>';
  try {
    const data = await api('/schedule');
    const jobs = data.jobs || [];
    if (jobs.length === 0) {
      listEl.innerHTML = '<div style="padding:10px; color:var(--text-muted);">No scheduled jobs. Click "+ Job" above.</div>';
      return;
    }
    listEl.innerHTML = jobs.map(j => `
      <div class="post-item" style="cursor:default;">
        <div class="post-title">${escapeHtml(j.action === 'generate' ? (j.topic || j.topic_id || 'Generation Job') : 'Publish Due Posts')}</div>
        <div class="post-meta" style="flex-wrap:wrap; margin-top:4px;">
          <span>🕒 ${j.run_at || 'now'}</span>
          <span>•</span>
          <span class="badge ${j.status === 'completed' ? 'badge-published' : j.status === 'running' ? 'badge-reviewed' : 'badge-draft'}">${j.status}</span>
          ${j.recurring ? `<span>(${j.recurring})</span>` : ''}
        </div>
        ${j.log ? `<div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">${escapeHtml(j.log)}</div>` : ''}
        <div style="display:flex; gap:6px; margin-top:6px;">
          <button class="btn btn-secondary" style="padding:2px 8px; font-size:0.7rem;" onclick="runJobNow('${j.id}')">Run Now</button>
          <button class="btn btn-secondary" style="padding:2px 8px; font-size:0.7rem; color:var(--red);" onclick="deleteJob('${j.id}')">Delete</button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    listEl.innerHTML = `<div style="color:var(--red); padding:10px;">Error: ${err.message}</div>`;
  }
}

function openScheduleModal() { openModal('scheduleModal'); }

function onSchedActionChange() {
  const isGen = document.getElementById('schedAction').value === 'generate';
  document.getElementById('schedGenFields').style.display = isGen ? 'block' : 'none';
}

async function addScheduleJob() {
  try {
    await api('/schedule/add', 'POST', {
      action: document.getElementById('schedAction').value,
      topic: document.getElementById('schedTopic').value,
      section: document.getElementById('schedSection').value,
      run_at: document.getElementById('schedRunAt').value,
      recurring: document.getElementById('schedRecurring').value,
      auto_push: document.getElementById('schedAutoPush').checked,
    });
    closeModal('scheduleModal');
    loadSchedule();
  } catch (err) {
    alert('Failed to add schedule: ' + err.message);
  }
}

async function toggleScheduler() {
  try {
    const res = await api('/schedule/toggle', 'POST', {});
    loadStatus();
  } catch (err) {
    alert('Toggle scheduler error: ' + err.message);
  }
}

async function runJobNow(id) {
  try {
    await api('/schedule/run-now', 'POST', { id });
    loadSchedule();
  } catch (err) {
    alert('Run job error: ' + err.message);
  }
}

async function deleteJob(id) {
  if (!confirm('Delete this scheduled job?')) return;
  try {
    await api('/schedule/delete', 'POST', { id });
    loadSchedule();
  } catch (err) {
    alert('Delete job error: ' + err.message);
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

