document.addEventListener('DOMContentLoaded', function() {
    const webcamElement = document.getElementById('webcam');
    const canvasElement = document.getElementById('canvas');
    const startButton = document.getElementById('startWebcam');
    const captureButton = document.getElementById('captureImage');
    const resultsDiv = document.getElementById('webcamResults');
    let stream = null;

    // Start the webcam
    async function startWebcam() {
        try {
            const constraints = {
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            };
            
            stream = await navigator.mediaDevices.getUserMedia(constraints);
            webcamElement.srcObject = stream;
            webcamElement.style.display = 'block';
            canvasElement.style.display = 'none';
            captureButton.disabled = false;
            startButton.textContent = 'Stop Webcam';
            startButton.classList.remove('btn-primary');
            startButton.classList.add('btn-danger');
            
            // Clear previous results
            resultsDiv.innerHTML = '';
            
        } catch (error) {
            console.error('Error accessing webcam:', error);
            alert('Error accessing webcam. Please make sure you have a webcam connected and have granted permission to use it.');
        }
    }

    // Stop the webcam
    function stopWebcam() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            webcamElement.srcObject = null;
            webcamElement.style.display = 'none';
            captureButton.disabled = true;
            startButton.textContent = 'Start Webcam';
            startButton.classList.remove('btn-danger');
            startButton.classList.add('btn-primary');
        }
    }

    // Toggle webcam
    startButton.addEventListener('click', function() {
        if (stream) {
            stopWebcam();
        } else {
            startWebcam();
        }
    });

    // Capture image from webcam
    captureButton.addEventListener('click', function() {
        if (!stream) return;
        
        // Show loading spinner
        resultsDiv.innerHTML = '<div class="text-center my-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Analyzing emotions...</p></div>';
        
        // Get canvas context and draw the current video frame
        const context = canvasElement.getContext('2d');
        canvasElement.width = webcamElement.videoWidth;
        canvasElement.height = webcamElement.videoHeight;
        context.drawImage(webcamElement, 0, 0, canvasElement.width, canvasElement.height);
        
        // Convert canvas to base64 image
        const imageData = canvasElement.toDataURL('image/jpeg');
        
        // Send image to the server for processing
        const formData = new FormData();
        formData.append('image', imageData);
        
        fetch('/webcam', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultsDiv.innerHTML = `<div class="alert alert-warning">${data.error}</div>`;
            } else {
                displayResults(data);
            }
        })
        .catch(error => {
            console.error('Error processing webcam image:', error);
            resultsDiv.innerHTML = `<div class="alert alert-danger">Error processing image: ${error.message}</div>`;
        });
    });

    // Display emotion detection results
    function displayResults(data) {
        const results = data.results;
        let html = '<div class="card my-4"><div class="card-header bg-primary text-white"><h5 class="mb-0">Emotion Detection Results</h5></div><div class="card-body">';
        
        if (results.length === 0) {
            html += '<div class="alert alert-warning">No faces detected</div>';
        } else {
            // Display the processed image
            html += `<div class="text-center mb-4"><img src="${data.image_url}" alt="Processed image" class="img-fluid rounded" style="max-height: 400px;"></div>`;
            
            html += '<div class="row">';
            results.forEach((result, index) => {
                const emotions = result.emotions;
                const dominantEmotion = result.dominant_emotion;
                const confidence = (result.confidence * 100).toFixed(2);
                
                html += `
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h6 class="mb-0">Face ${index + 1}</h6>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">Dominant Emotion: <span class="badge bg-primary">${dominantEmotion}</span></h5>
                            <p class="card-text">Confidence: ${confidence}%</p>
                            <h6>All Emotions:</h6>
                            <ul class="list-group">
                `;
                
                // Sort emotions by confidence
                const sortedEmotions = Object.entries(emotions).sort((a, b) => b[1] - a[1]);
                
                sortedEmotions.forEach(([emotion, score]) => {
                    const scorePercentage = (score * 100).toFixed(2);
                    const isActive = emotion === dominantEmotion ? 'active' : '';
                    html += `
                    <li class="list-group-item d-flex justify-content-between align-items-center ${isActive}">
                        ${emotion}
                        <span class="badge bg-primary rounded-pill">${scorePercentage}%</span>
                    </li>
                    `;
                });
                
                html += `
                            </ul>
                        </div>
                    </div>
                </div>
                `;
            });
            html += '</div>';
        }
        
        html += '</div></div>';
        resultsDiv.innerHTML = html;
    }
});
