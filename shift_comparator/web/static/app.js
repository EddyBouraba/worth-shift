// État de l'application
let currentShifts = [];
let scenarios = [];

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    // Définir la date par défaut à aujourd'hui
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('shift-date').value = today;

    // Charger les scénarios sauvegardés
    loadScenarios();
});

// Navigation entre onglets
function showTab(tabName) {
    // Cacher tous les onglets
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));

    // Désactiver tous les boutons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));

    // Activer l'onglet sélectionné
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');

    // Charger les scénarios si on va sur l'onglet comparaison
    if (tabName === 'compare') {
        loadScenarios();
    }
}

// Ajouter un shift
function addShift() {
    const date = document.getElementById('shift-date').value;
    const type = document.getElementById('shift-type').value;

    if (!date) {
        showMessage('Veuillez sélectionner une date', 'error');
        return;
    }

    // Ajouter à la liste
    currentShifts.push({ date, type });

    // Afficher
    renderShiftsList();

    // Incrémenter la date pour le prochain shift
    const nextDate = new Date(date);
    nextDate.setDate(nextDate.getDate() + 1);
    document.getElementById('shift-date').value = nextDate.toISOString().split('T')[0];

    // Message de succès
    showMessage('Shift ajouté!', 'success', 2000);
}

// Retirer un shift
function removeShift(index) {
    currentShifts.splice(index, 1);
    renderShiftsList();
}

// Effacer tous les shifts
function clearShifts() {
    if (currentShifts.length === 0) {
        return;
    }

    if (confirm('Effacer tous les shifts?')) {
        currentShifts = [];
        renderShiftsList();
    }
}

// Afficher la liste des shifts
function renderShiftsList() {
    const container = document.getElementById('shifts-list');
    const countSpan = document.getElementById('shift-count');

    countSpan.textContent = currentShifts.length;

    if (currentShifts.length === 0) {
        container.innerHTML = '<p class="placeholder">Aucun shift ajouté</p>';
        return;
    }

    container.innerHTML = currentShifts.map((shift, index) => `
        <div class="shift-item">
            <div class="shift-info">
                <div class="shift-date">${formatDate(shift.date)}</div>
                <div class="shift-type">${getShiftTypeLabel(shift.type)}</div>
            </div>
            <button class="shift-remove" onclick="removeShift(${index})">🗑️</button>
        </div>
    `).join('');
}

// Calculer le scénario
async function calculateScenario() {
    if (currentShifts.length === 0) {
        showMessage('Veuillez ajouter au moins un shift', 'error');
        return;
    }

    const name = document.getElementById('scenario-name').value || 'Scénario';
    const hourlyRate = parseFloat(document.getElementById('hourly-rate').value);

    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                hourly_rate: hourlyRate,
                shifts: currentShifts
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur de calcul');
        }

        const result = await response.json();
        displayResult(result);

    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

// Sauvegarder le scénario
async function saveScenario() {
    const name = document.getElementById('scenario-name').value.trim();

    if (!name) {
        showMessage('Veuillez entrer un nom pour le scénario', 'error');
        return;
    }

    if (currentShifts.length === 0) {
        showMessage('Veuillez ajouter au moins un shift', 'error');
        return;
    }

    const hourlyRate = parseFloat(document.getElementById('hourly-rate').value);

    try {
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                hourly_rate: hourlyRate,
                shifts: currentShifts
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur de sauvegarde');
        }

        const result = await response.json();
        showMessage('Scénario "' + name + '" sauvegardé!', 'success');

        // Recharger la liste des scénarios
        await loadScenarios();

    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

// Charger les scénarios sauvegardés
async function loadScenarios() {
    try {
        const response = await fetch('/api/scenarios');

        if (!response.ok) {
            throw new Error('Erreur de chargement');
        }

        const data = await response.json();
        scenarios = data.scenarios;
        renderSavedScenarios();

    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

// Afficher les scénarios sauvegardés
function renderSavedScenarios() {
    const container = document.getElementById('saved-scenarios');

    if (scenarios.length === 0) {
        container.innerHTML = '<p class="placeholder">Aucun scénario sauvegardé. Créez-en dans l\'onglet précédent.</p>';
        return;
    }

    container.innerHTML = scenarios.map((scenario, index) => `
        <div class="scenario-item">
            <input type="checkbox" id="scenario-${scenario.id}" data-id="${scenario.id}">
            <div class="scenario-info">
                <div class="scenario-name">${scenario.name}</div>
                <div class="scenario-details">
                    ${scenario.days} jour(s) • ${scenario.hourly_rate}€/h
                </div>
            </div>
        </div>
    `).join('');
}

// Supprimer les scénarios sélectionnés
async function deleteSelectedScenarios() {
    const checkboxes = document.querySelectorAll('#saved-scenarios input[type="checkbox"]:checked');

    if (checkboxes.length === 0) {
        showMessage('Aucun scénario sélectionné', 'error');
        return;
    }

    if (!confirm(`Supprimer ${checkboxes.length} scénario(s)?`)) {
        return;
    }

    const ids = Array.from(checkboxes).map(cb => parseInt(cb.dataset.id));

    try {
        const response = await fetch('/api/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_ids: ids })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur de suppression');
        }

        showMessage('Scénarios supprimés', 'success');
        await loadScenarios();

    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

// Comparer les scénarios sélectionnés
async function compareScenarios() {
    const checkboxes = document.querySelectorAll('#saved-scenarios input[type="checkbox"]:checked');

    if (checkboxes.length < 2) {
        showMessage('Veuillez sélectionner au moins 2 scénarios', 'error');
        return;
    }

    const ids = Array.from(checkboxes).map(cb => parseInt(cb.dataset.id));

    try {
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_ids: ids })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur de comparaison');
        }

        const result = await response.json();
        displayComparison(result);

    } catch (error) {
        showMessage('Erreur: ' + error.message, 'error');
    }
}

// Afficher le résultat d'un calcul
function displayResult(result) {
    const container = document.getElementById('result');

    const breakdown = result.breakdown;
    let output = '';

    output += '═══════════════════════════════════════════════════════\n';
    output += `SCÉNARIO: ${result.name}\n`;
    output += `Taux horaire: ${result.hourly_rate.toFixed(2)}€/h\n`;
    output += '═══════════════════════════════════════════════════════\n\n';

    output += 'DÉTAIL PAR JOUR:\n';
    output += '───────────────────────────────────────────────────────\n';

    result.days.forEach(day => {
        output += `\n${formatDate(day.date)} (${day.day_name}) - ${getShiftTypeLabel(day.shift_type)}\n`;
        output += `  Heures: ${day.hours.toFixed(2)}h\n`;
        output += `  Rémunération: ${day.pay.toFixed(2)}€\n`;
        if (day.bonus > 0) {
            output += `  Majorations: ${day.bonus.toFixed(2)}€\n`;
        }
    });

    output += '\n═══════════════════════════════════════════════════════\n';
    output += 'RÉSUMÉ GLOBAL\n';
    output += '═══════════════════════════════════════════════════════\n';

    if (breakdown.normal > 0) {
        output += `Heures normales:         ${breakdown.normal.toFixed(2)}h\n`;
    }
    if (breakdown.night > 0) {
        output += `Heures de nuit (+15%):   ${breakdown.night.toFixed(2)}h\n`;
    }
    if (breakdown.sunday > 0) {
        output += `Heures dimanche (+25%):  ${breakdown.sunday.toFixed(2)}h\n`;
    }
    if (breakdown.night_sunday > 0) {
        output += `Heures nuit+dim (+40%):  ${breakdown.night_sunday.toFixed(2)}h\n`;
    }

    output += `\nTotal heures travaillées: ${result.total_hours.toFixed(2)}h\n`;
    output += `Total majorations:        ${result.total_bonus.toFixed(2)}€\n`;
    output += `\n✨ RÉMUNÉRATION TOTALE:    ${result.total_pay.toFixed(2)}€\n`;
    output += '═══════════════════════════════════════════════════════\n';

    container.textContent = output;
}

// Afficher le résultat d'une comparaison
function displayComparison(result) {
    const container = document.getElementById('compare-result');

    let output = '';

    output += '═══════════════════════════════════════════════════════\n';
    output += 'CLASSEMENT DES SCÉNARIOS\n';
    output += '═══════════════════════════════════════════════════════\n\n';

    output += 'Rang | Scénario                  | Heures  | Rémunération | Écart\n';
    output += '─────┼───────────────────────────┼─────────┼──────────────┼────────\n';

    result.ranking.forEach(item => {
        const rank = item.rank.toString().padStart(2);
        const name = item.name.padEnd(25).substring(0, 25);
        const hours = item.hours.toFixed(2).padStart(6) + 'h';
        const pay = item.pay.toFixed(2).padStart(9) + '€';
        const diff = item.difference === 0
            ? 'MEILLEUR'
            : '-' + item.difference.toFixed(2) + '€';
        const pct = '(' + item.percentage.toFixed(1) + '%)';

        output += `${rank}   | ${name} | ${hours} | ${pay}   | ${diff} ${pct}\n`;
    });

    output += '\n═══════════════════════════════════════════════════════\n';
    output += '🏆 MEILLEUR SCÉNARIO\n';
    output += '═══════════════════════════════════════════════════════\n';
    output += `\n${result.best.name}\n`;
    output += `  → ${result.best.total_pay.toFixed(2)}€ pour ${result.best.total_hours.toFixed(2)}h\n`;
    output += `  → Majorations: ${result.best.total_bonus.toFixed(2)}€\n\n`;

    if (result.ranking.length > 1) {
        const worst = result.ranking[result.ranking.length - 1];
        const gain = result.best.total_pay - worst.pay;
        output += `💰 Gain par rapport au pire scénario: ${gain.toFixed(2)}€\n`;
    }

    output += '═══════════════════════════════════════════════════════\n';

    container.textContent = output;

    // Afficher un message de notification
    showMessage(
        `✓ Meilleur scénario: "${result.best.name}" (${result.best.total_pay.toFixed(2)}€)`,
        'success',
        5000
    );
}

// Afficher un message
function showMessage(text, type = 'success', duration = 3000) {
    // Créer le message
    const message = document.createElement('div');
    message.className = `message message-${type}`;
    message.textContent = text;

    // Ajouter au body
    document.body.appendChild(message);

    // Style inline pour le positionnement
    message.style.position = 'fixed';
    message.style.top = '20px';
    message.style.right = '20px';
    message.style.zIndex = '10000';
    message.style.minWidth = '300px';
    message.style.animation = 'slideInRight 0.3s';

    // Retirer après la durée
    setTimeout(() => {
        message.style.animation = 'slideOutRight 0.3s';
        setTimeout(() => message.remove(), 300);
    }, duration);
}

// Formater une date
function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('fr-FR', options);
}

// Obtenir le label d'un type de shift
function getShiftTypeLabel(type) {
    const labels = {
        'MATIN': 'MATIN (06:00-15:00)',
        'APRES_MIDI': 'APRÈS-MIDI (14:00-23:00)',
        'NUIT': 'NUIT (22:00-07:00)'
    };
    return labels[type] || type;
}

// Animations CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
