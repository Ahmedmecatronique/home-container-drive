/****************************************************
 * HOME CONTAINER DRIVE – APP.JS
 ****************************************************/

const API_BASE = window.location.origin;

// État global
let currentUser = null;
let currentRole = null;
let currentToken = null;

function $(id) {
    return document.getElementById(id);
}

/****************************************************
 * AUTH : changement de vues (login / register / forgot)
 ****************************************************/

function showAuthView(viewName) {
    const views = document.querySelectorAll(".auth-view");
    views.forEach(v => {
        v.classList.toggle("hidden", v.dataset.view !== viewName);
    });

    const tabs = document.querySelectorAll(".auth-tab");
    tabs.forEach(tab => {
        tab.classList.toggle("active", tab.id === "tab-" + viewName);
    });

    const statusEl = $("auth-status");
    if (statusEl) {
        statusEl.textContent = "";
        statusEl.className = "status";
    }
}

function hideAuthOverlay() {
    const overlay = $("auth-overlay");
    if (overlay) overlay.style.display = "none";
}

function showAuthOverlay() {
    const overlay = $("auth-overlay");
    if (overlay) overlay.style.display = "flex";
}

/****************************************************
 * LOGIN / REGISTER / FORGOT
 ****************************************************/

function updateHeaderBadge() {
    // si un jour tu remets un badge dans la topbar
}

/* ---------- LOGIN ---------- */

async function loginWithCredentials(username, password, statusEl) {
    if (!statusEl) statusEl = $("auth-status");

    if (!username || !password) {
        statusEl.textContent = "Username et mot de passe requis.";
        statusEl.className = "status status-error";
        return;
    }

    statusEl.textContent = "Connexion en cours...";
    statusEl.className = "status status-info";

    try {
        const resp = await fetch(API_BASE + "/auth/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ username, password })
        });

        if (!resp.ok) {
            statusEl.textContent = "Identifiants invalides.";
            statusEl.className = "status status-error";
            return;
        }

        const data = await resp.json();
        currentUser  = data.username;
        currentRole  = data.role;
        currentToken = data.access_token;

        statusEl.textContent = `Connecté en tant que ${currentUser} (${currentRole})`;
        statusEl.className = "status status-success";

        // Afficher le bouton menu, mais laisser la sidebar FERMÉE
        const menuBtn  = $("menu-btn");
        const sidebar  = $("sidebar");
        const appShell = document.querySelector(".app-shell");

        if (menuBtn)  menuBtn.style.display = "block";
        if (sidebar)  sidebar.classList.remove("open");
        if (appShell) appShell.style.marginLeft = "0";

        hideAuthOverlay();

        const refreshBtn = $("refresh-files");
        if (refreshBtn) refreshBtn.disabled = false;

        refreshFiles();
    } catch (err) {
        console.error(err);
        statusEl.textContent = "Erreur de connexion au serveur.";
        statusEl.className = "status status-error";
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const username = $("login-username")?.value.trim();
    const password = $("login-password")?.value;
    const statusEl = $("auth-status");
    await loginWithCredentials(username, password, statusEl);
}

/* ---------- REGISTER ---------- */

async function handleRegister(event) {
    event.preventDefault();
    const username  = $("register-username")?.value.trim();
    const password  = $("register-password")?.value;
    const password2 = $("register-password2")?.value;

    const statusEl = $("auth-status");

    if (!username || !password) {
        statusEl.textContent = "Tous les champs sont obligatoires.";
        statusEl.className  = "status status-error";
        return;
    }

    if (password !== password2) {
        statusEl.textContent = "Les mots de passe ne correspondent pas.";
        statusEl.className  = "status status-error";
        return;
    }

    statusEl.textContent = "Création du compte...";
    statusEl.className  = "status status-info";

    try {
        const resp = await fetch(API_BASE + "/auth/register", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ username, password })
        });

        if (!resp.ok) {
            const errData = await resp.json().catch(() => ({}));
            statusEl.textContent = errData.detail || "Erreur lors de la création du compte.";
            statusEl.className  = "status status-error";
            return;
        }

        statusEl.textContent = "Compte créé avec succès. Tu peux maintenant te connecter.";
        statusEl.className  = "status status-success";

        setTimeout(() => showAuthView("login"), 800);
    } catch (err) {
        console.error(err);
        statusEl.textContent = "Erreur réseau lors de la création du compte.";
        statusEl.className  = "status status-error";
    }
}

/* ---------- FORGOT ---------- */

async function handleForgot(event) {
    event.preventDefault();

    const fullname = $("forgot-fullname")?.value.trim();
    const username = $("forgot-username")?.value.trim();
    const phone    = $("forgot-phone")?.value.trim();

    const statusEl = $("auth-status");

    if (!fullname || !username || !phone) {
        statusEl.textContent = "Merci de remplir tous les champs.";
        statusEl.className  = "status status-error";
        return;
    }

    statusEl.textContent =
        `Demande enregistrée pour "${fullname}" (${username}), contact : ${phone}. L'administrateur vérifiera.`;
    statusEl.className  = "status status-info";
}

/****************************************************
 * WORKSPACE (liste / upload / download)
 ****************************************************/

async function refreshFiles() {
    const listEl = $("files-list");
    if (!listEl) return;

    listEl.className = "files-list";
    listEl.innerHTML = "<p>Chargement...</p>";

    try {
        const headers = {};
        if (currentToken) headers["Authorization"] = "Bearer " + currentToken;

        const resp = await fetch(API_BASE + "/workspace/files", {
            method: "GET",
            headers
        });

        if (!resp.ok) {
            listEl.className = "files-list empty";
            listEl.innerHTML = "<p>Impossible de récupérer les fichiers.</p>";
            return;
        }

        const data = await resp.json();

        if (!Array.isArray(data) || data.length === 0) {
            listEl.className = "files-list empty";
            listEl.innerHTML = "<p>Aucun fichier dans le workspace.</p>";
            return;
        }

        const rows = data.map(f => `
            <div class="file-row">
                <div class="file-name">${f.filename}</div>
                <div class="file-meta">
                    <span>Owner : ${f.owner}</span>
                    <span>Créé : ${f.created_at ? new Date(f.created_at).toLocaleString() : ""}</span>
                </div>
                <div class="file-actions">
                    <button class="btn btn-outline btn-xs" onclick="viewFile(${f.id})">Voir</button>
                    <button class="btn btn-secondary btn-xs" onclick="downloadFile(${f.id}, '${f.filename}')">Télécharger</button>
                </div>
            </div>
        `).join("");

        listEl.innerHTML = rows;
    } catch (err) {
        console.error(err);
        listEl.className = "files-list empty";
        listEl.innerHTML = "<p>Erreur lors de la récupération des fichiers.</p>";
    }
}

async function handleFileInput(event) {
    const input = event.target;
    if (!input.files || input.files.length === 0) return;

    if (!currentUser) {
        alert("Tu dois être connecté.");
        input.value = "";
        return;
    }

    const file = input.files[0];
    const formData = new FormData();
    formData.append("username", currentUser);
    formData.append("uploaded_file", file);

    try {
        const headers = {};
        if (currentToken) headers["Authorization"] = "Bearer " + currentToken;

        const resp = await fetch(API_BASE + "/workspace/upload", {
            method: "POST",
            headers,
            body: formData
        });

        if (!resp.ok) {
            alert("Erreur upload.");
        } else {
            alert("Upload OK.");
            refreshFiles();
        }
    } catch (err) {
        console.error(err);
        alert("Erreur réseau.");
    }

    input.value = "";
}

function viewFile(id) {
    window.open(API_BASE + "/workspace/download/" + id, "_blank");
}

function downloadFile(id, filename) {
    const url = API_BASE + "/workspace/download/" + id;
    const a = document.createElement("a");
    a.href = url;
    a.download = filename || "download";
    document.body.appendChild(a);
    a.click();
    a.remove();
}

window.viewFile = viewFile;
window.downloadFile = downloadFile;

/****************************************************
 * NAVIGATION SECTIONS (Dashboard / Workspace / Privé / Chat / Settings)
 ****************************************************/

function showSection(sectionName) {
    const sections = document.querySelectorAll(".page-section");
    sections.forEach(sec => sec.classList.add("hidden"));

    const target = $("section-" + sectionName);
    if (target) target.classList.remove("hidden");
}

/****************************************************
 * INIT GLOBAL (DOM READY)
 ****************************************************/

document.addEventListener("DOMContentLoaded", () => {
    /***** Auth tabs *****/
    $("tab-login")?.addEventListener("click", () => showAuthView("login"));
    $("tab-register")?.addEventListener("click", () => showAuthView("register"));
    $("tab-forgot")?.addEventListener("click", () => showAuthView("forgot"));

    /***** Auth forms *****/
    $("login-form")?.addEventListener("submit", handleLogin);
    $("register-form")?.addEventListener("submit", handleRegister);
    $("forgot-form")?.addEventListener("submit", handleForgot);

    /***** Workspace *****/
    $("refresh-files")?.addEventListener("click", refreshFiles);
    $("file-input")?.addEventListener("change", handleFileInput);

    /***** Sidebar navigation *****/
    const sidebarButtons = document.querySelectorAll(".sidebar-item");
    const appShell       = document.querySelector(".app-shell");
    const sidebar        = $("sidebar");
    const overlay        = $("sidebar-overlay");
    const menuBtn        = $("menu-btn");

    sidebarButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            // visuel actif
            sidebarButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            // afficher la bonne section
            const section = btn.dataset.section;
            showSection(section);

            // Si on va sur la section settings, charger les préférences
            if (section === "settings") {
                if (currentUser) loadSettings();
            }

            // refermer le menu après clic
            if (sidebar && appShell) {
                sidebar.classList.remove("open");
                appShell.style.marginLeft = "0";
            }
            if (overlay) overlay.classList.remove("show");
        });
    });

    /***** Déconnexion *****/
    $("logout-btn")?.addEventListener("click", () => {
        currentUser  = null;
        currentRole  = null;
        currentToken = null;

        showAuthOverlay();

        if (menuBtn)  menuBtn.style.display = "none";
        if (sidebar)  sidebar.classList.remove("open");
        if (appShell) appShell.style.marginLeft = "0";
        if (overlay)  overlay.classList.remove("show");

        showSection("workspace");
    });

    /***** Menu hamburger : ouvre / ferme la sidebar + pousse la page *****/
    if (menuBtn && sidebar && appShell) {
        menuBtn.addEventListener("click", () => {
            const isOpen = sidebar.classList.toggle("open");
            appShell.style.marginLeft = isOpen ? "260px" : "0";
            if (overlay) overlay.classList.toggle("show", isOpen);
        });
    }

    // Si tu crées un overlay en HTML, clique dessus pour fermer le menu :
    if (overlay && sidebar && appShell) {
        overlay.addEventListener("click", () => {
            sidebar.classList.remove("open");
            overlay.classList.remove("show");
            appShell.style.marginLeft = "0";
        });
    }

    /***** SETTINGS: charge / sauvegarde / mot de passe / blocages *****/
    async function loadSettings() {
        const statusEl = $("settings-status");
        if (!statusEl) return;
        if (!currentUser) {
            statusEl.textContent = "Connecte-toi pour accéder aux paramètres.";
            statusEl.className = "status status-error";
            return;
        }
        statusEl.textContent = "Chargement...";
        statusEl.className = "status status-info";
        try {
            const resp = await fetch(API_BASE + "/auth/settings/" + encodeURIComponent(currentUser));
            if (!resp.ok) {
                statusEl.textContent = "Impossible de charger les paramètres.";
                statusEl.className = "status status-error";
                return;
            }
            const data = await resp.json();
            const s = data.settings || {};
            $("setting-theme").value = s.theme || "light";
            $("setting-language").value = s.language || "fr";
            $("setting-notifications").checked = !!s.notifications;
            $("setting-default-path").value = s.default_path || "";
            renderBlockedList(s.blocked || []);
            statusEl.textContent = "Paramètres chargés.";
            statusEl.className = "status status-success";
        } catch (err) {
            console.error(err);
            statusEl.textContent = "Erreur réseau.";
            statusEl.className = "status status-error";
        }
    }

    async function saveSettings() {
        const statusEl = $("settings-status");
        if (!statusEl) return;
        if (!currentUser) {
            statusEl.textContent = "Connecte-toi.";
            statusEl.className = "status status-error";
            return;
        }
        const payload = {
            username: currentUser,
            settings: {
                theme: $("setting-theme").value,
                language: $("setting-language").value,
                notifications: !!$("setting-notifications").checked,
                default_path: $("setting-default-path").value.trim()
            }
        };
        statusEl.textContent = "Enregistrement...";
        statusEl.className = "status status-info";
        try {
            const resp = await fetch(API_BASE + "/auth/settings/update", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload)
            });
            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                statusEl.textContent = err.detail || "Erreur lors de la sauvegarde.";
                statusEl.className = "status status-error";
                return;
            }
            const data = await resp.json();
            statusEl.textContent = "Paramètres sauvegardés.";
            statusEl.className = "status status-success";
            renderBlockedList(data.settings.blocked || []);
        } catch (err) {
            console.error(err);
            statusEl.textContent = "Erreur réseau";
            statusEl.className = "status status-error";
        }
    }

    function renderBlockedList(list) {
        const el = $("blocked-list");
        if (!el) return;
        if (!list || list.length === 0) {
            el.textContent = "Aucun utilisateur bloqué.";
        } else {
            el.innerHTML = list.map(u => `<div>${u}</div>`).join("");
        }
    }

    async function handleChangePassword(e) {
        e.preventDefault();
        const status = $("change-password-status");
        const oldp = $("old-password").value;
        const newp = $("new-password").value;
        const newp2 = $("new-password2").value;
        if (!oldp || !newp) { status.textContent = "Remplis tous les champs."; status.className = "status status-error"; return; }
        if (newp !== newp2) { status.textContent = "Les nouveaux mots de passe ne correspondent pas."; status.className = "status status-error"; return; }
        status.textContent = "Modification en cours..."; status.className = "status status-info";
        try {
            const resp = await fetch(API_BASE + "/auth/change_password", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username: currentUser, old_password: oldp, new_password: newp})
            });
            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                status.textContent = err.detail || "Erreur";
                status.className = "status status-error";
                return;
            }
            status.textContent = "Mot de passe modifié.";
            status.className = "status status-success";
            $("old-password").value = ""; $("new-password").value = ""; $("new-password2").value = "";
        } catch (err) {
            console.error(err);
            status.textContent = "Erreur réseau";
            status.className = "status status-error";
        }
    }

    async function blockUser(action) {
        const target = $("block-target").value.trim();
        if (!target) { alert("Entrez un nom d’utilisateur."); return; }
        try {
            const resp = await fetch(API_BASE + "/auth/block_user", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username: currentUser, target, action})
            });
            if (!resp.ok) { const err = await resp.json().catch(() => ({})); alert(err.detail || "Erreur"); return; }
            const data = await resp.json();
            renderBlockedList(data.blocked || []);
            $("block-target").value = "";
        } catch (err) { console.error(err); alert("Erreur réseau"); }
    }

    // listeners
    $("save-settings")?.addEventListener("click", saveSettings);
    $("change-password-form")?.addEventListener("submit", handleChangePassword);
    $("block-btn")?.addEventListener("click", (e) => { e.preventDefault(); blockUser('block'); });
    $("unblock-btn")?.addEventListener("click", (e) => { e.preventDefault(); blockUser('unblock'); });

    /***** Au démarrage : overlay login *****/
    if (menuBtn) menuBtn.style.display = "none"; // caché avant login
    showAuthOverlay();
    updateHeaderBadge();
    showSection("workspace"); // section par défaut
});
