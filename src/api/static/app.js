// DOM Elements
const elements = {
    // Tabs
    tabs: document.querySelectorAll('.tab'),
    vectorTab: document.getElementById('vector-tab'),
    animeTab: document.getElementById('anime-tab'),

    // Forms
    vectorForm: document.getElementById('vector-form'),
    animeForm: document.getElementById('anime-form'),

    // Vector inputs
    vectorPrompt: document.getElementById('vector-prompt'),
    vectorLora: document.getElementById('vector-lora'),
    vectorWidth: document.getElementById('vector-width'),
    vectorHeight: document.getElementById('vector-height'),
    vectorSteps: document.getElementById('vector-steps'),
    vectorStepsValue: document.getElementById('vector-steps-value'),
    vectorGuidance: document.getElementById('vector-guidance'),
    vectorGuidanceValue: document.getElementById('vector-guidance-value'),
    vectorSeed: document.getElementById('vector-seed'),

    // Anime inputs
    animeImage: document.getElementById('anime-image'),
    animeDrop: document.getElementById('anime-drop'),
    animePreview: document.getElementById('anime-preview'),
    animeStyle: document.getElementById('anime-style'),
    animeStrength: document.getElementById('anime-strength'),
    animeStrengthValue: document.getElementById('anime-strength-value'),
    animeSteps: document.getElementById('anime-steps'),
    animeStepsValue: document.getElementById('anime-steps-value'),
    animeSeed: document.getElementById('anime-seed'),
    animePrompt: document.getElementById('anime-prompt'),

    // Result
    resultSection: document.getElementById('result-section'),
    resultImage: document.getElementById('result-image'),
    downloadBtn: document.getElementById('download-btn'),
    newBtn: document.getElementById('new-btn'),

    // Loading
    loading: document.getElementById('loading'),
    loadingText: document.getElementById('loading-text'),

    // Error
    error: document.getElementById('error'),
    errorText: document.getElementById('error-text'),
    errorDismiss: document.getElementById('error-dismiss'),
};

// State
let currentBlob = null;
let currentFilename = 'generated.png';

// Tab switching
elements.tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        elements.tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        const tabName = tab.dataset.tab;
        elements.vectorTab.classList.toggle('active', tabName === 'vector');
        elements.animeTab.classList.toggle('active', tabName === 'anime');
    });
});

// Range input value display
elements.vectorSteps.addEventListener('input', (e) => {
    elements.vectorStepsValue.textContent = e.target.value;
});
elements.vectorGuidance.addEventListener('input', (e) => {
    elements.vectorGuidanceValue.textContent = e.target.value;
});
elements.animeStrength.addEventListener('input', (e) => {
    elements.animeStrengthValue.textContent = e.target.value;
});
elements.animeSteps.addEventListener('input', (e) => {
    elements.animeStepsValue.textContent = e.target.value;
});

// File drop zone
elements.animeDrop.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.animeDrop.classList.add('dragover');
});

elements.animeDrop.addEventListener('dragleave', () => {
    elements.animeDrop.classList.remove('dragover');
});

elements.animeDrop.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.animeDrop.classList.remove('dragover');

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        elements.animeImage.files = e.dataTransfer.files;
        showPreview(file);
    }
});

elements.animeImage.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        showPreview(file);
    }
});

function showPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        elements.animePreview.src = e.target.result;
        elements.animePreview.classList.add('visible');
    };
    reader.readAsDataURL(file);
}

// Form submissions
elements.vectorForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await generateVector();
});

elements.animeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await generateAnime();
});

async function generateVector() {
    const formData = new FormData();
    formData.append('prompt', elements.vectorPrompt.value);
    formData.append('lora', elements.vectorLora.value);
    formData.append('width', elements.vectorWidth.value);
    formData.append('height', elements.vectorHeight.value);
    formData.append('steps', elements.vectorSteps.value);
    formData.append('guidance', elements.vectorGuidance.value);

    if (elements.vectorSeed.value) {
        formData.append('seed', elements.vectorSeed.value);
    }

    await submitGeneration('/generate/vector', formData, 'Generating vector graphic...');
}

async function generateAnime() {
    const formData = new FormData();
    formData.append('image', elements.animeImage.files[0]);
    formData.append('style', elements.animeStyle.value);
    formData.append('strength', elements.animeStrength.value);
    formData.append('steps', elements.animeSteps.value);

    if (elements.animeSeed.value) {
        formData.append('seed', elements.animeSeed.value);
    }
    if (elements.animePrompt.value) {
        formData.append('prompt', elements.animePrompt.value);
    }

    await submitGeneration('/generate/anime', formData, 'Converting to anime style...');
}

async function submitGeneration(endpoint, formData, loadingMessage) {
    showLoading(loadingMessage);
    hideError();

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || `HTTP ${response.status}`);
        }

        currentBlob = await response.blob();
        currentFilename = `okgraphics_${Date.now()}.png`;

        const url = URL.createObjectURL(currentBlob);
        elements.resultImage.src = url;
        elements.resultSection.classList.remove('hidden');

        // Scroll to result
        elements.resultSection.scrollIntoView({ behavior: 'smooth' });

    } catch (err) {
        showError(err.message);
    } finally {
        hideLoading();
    }
}

// Download
elements.downloadBtn.addEventListener('click', () => {
    if (!currentBlob) return;

    const url = URL.createObjectURL(currentBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = currentFilename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// New generation
elements.newBtn.addEventListener('click', () => {
    elements.resultSection.classList.add('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Loading helpers
function showLoading(message) {
    elements.loadingText.textContent = message;
    elements.loading.classList.remove('hidden');
}

function hideLoading() {
    elements.loading.classList.add('hidden');
}

// Error helpers
function showError(message) {
    elements.errorText.textContent = message;
    elements.error.classList.remove('hidden');
}

function hideError() {
    elements.error.classList.add('hidden');
}

elements.errorDismiss.addEventListener('click', hideError);
