const fileInput = document.getElementById('file');
const uploadBtn = document.getElementById('upload-btn');
const resetBtn = document.getElementById('reset-btn');
const canvas = document.getElementById('canvas');

uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (file.type.startsWith('image/')) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.status === 'success') {
            const image = new Image();
            image.src = result.image;
            image.onload = () => {
                canvas.width = image.width;
                canvas.height = image.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(image, 0, 0, image.width, image.height);
                canvas.style.display = 'block';
            };
        } else {
            alert(result.detail);
        }
    } else {
        alert('Please select an image file.');
    }
});

histogramBtn.addEventListener('click', () => {
    // TODO: Implement histogram functionality
});

resetBtn.addEventListener('click', () => {
    fileInput.value = '';
    canvas.style.display = 'none';
});