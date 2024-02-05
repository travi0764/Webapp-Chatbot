
// ==================================================================================================

// function uploadData() {
//     const uploadInput = document.getElementById('upload');
//     const progressContainer = document.getElementById('progress-container');
//     const progressBar = document.getElementById('progress-bar');
//     const progressText = document.getElementById('progress-text');
//     const uploadMessage = document.getElementById('upload-message');

//     // Reset progress bar and message
//     progressBar.style.width = '0';
//     progressText.innerText = '0%';
//     uploadMessage.innerText = '';

//     const formData = new FormData(document.getElementById('uploadForm'));

//     // Make a POST request to the Flask backend route with AJAX
//     const xhr = new XMLHttpRequest();

//     xhr.upload.onprogress = function (event) {
//         if (event.lengthComputable) {
//             const percentComplete = (event.loaded / event.total) * 100;
//             progressBar.style.width = percentComplete + '%';
//             progressText.innerText = percentComplete.toFixed(2) + '%';
//         }
//     };

//     xhr.onreadystatechange = function () {
//         if (xhr.readyState === XMLHttpRequest.DONE) {
//             if (xhr.status === 200) {
//                 // Display the response from the upload API
//                 const response = JSON.parse(xhr.responseText);
//                 uploadMessage.innerText = response.message;
//             } else {
//                 // Upload failed
//                 uploadMessage.innerText = 'Upload failed. Please try again.';
//             }
//         }
//     };

//     xhr.open('POST', '/upload-data', true);
//     xhr.send(formData);
// }
// ================================================================================================

function askQuestion() {
    const questionInput = document.getElementById('question');
    const conversationContainer = document.getElementById('conversation-container');

    const question = questionInput.value.trim();

    // Add a new line for the user's query to the conversation container
    conversationContainer.innerHTML += `<div>User: ${question}</div>`;
    conversationContainer.innerHTML += `Bot: `;

    // Make a POST request to the server
    fetch(`/ask-question?question=${encodeURIComponent(question)}`, {
        method: 'POST',
    })
    .then(response => {
        // Check if the response is a readable stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');

        // Define a function to process the result of reading the stream
        function processResult(result) {
            if (result.done) return; // If the stream is done, exit the function

            // Decode the token from the result
            let token = decoder.decode(result.value);

            // Append the bot's response to a new line in the conversation container
            conversationContainer.innerHTML += `${token}`;

            // Scroll to the bottom to show the latest messages
            conversationContainer.scrollTop = conversationContainer.scrollHeight;

            // Continue reading the stream
            return reader.read().then(processResult);
        }



        // Start reading the stream and process the result
        return reader.read().then(processResult);
    })

    
    .catch(error => {
        // Log an error message if there's an issue with the fetch
        console.error('Error:', error);
    })
    .finally(() => {
        // Clear the input field after processing the user's question
        conversationContainer.innerHTML += `<div></div>`;

        questionInput.value = '';
    });
}

// Enable Enter key to trigger askQuestion
document.getElementById('question').addEventListener('keypress', function (e) {
    // If the Enter key is pressed, call the askQuestion function
    if (e.key === 'Enter') {
        askQuestion();
    }
});

// ================================================================================================

function uploadData() {
    // Get DOM elements
    const uploadInput = document.getElementById('upload');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const uploadMessage = document.getElementById('upload-message');

    // Reset progress bar and message
    resetProgress();

    // Create FormData object from the form
    const formData = new FormData(document.getElementById('uploadForm'));

    // Create XMLHttpRequest
    const xhr = new XMLHttpRequest();

    // Set up event listeners
    xhr.upload.onprogress = updateProgress;
    xhr.onreadystatechange = handleUploadResponse;

    // Open and send the request
    xhr.open('POST', '/upload-data', true);
    xhr.send(formData);

    // Function to update progress bar during file upload
    function updateProgress(event) {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            progressBar.style.width = `${percentComplete}%`;
            progressText.innerText = `${percentComplete.toFixed(2)}%`;
        }
    }

    // Function to handle the response from the server
    function handleUploadResponse() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            // Reset progress bar and message
            resetProgress();
    
            if (xhr.status === 200) {
                // Display success message
                const response = JSON.parse(xhr.responseText);
                uploadMessage.innerText = response.message;
            } else {
                // Display failure message
                uploadMessage.innerText = 'Upload failed. Please try again.';
            }
        }
    }
    

    // Function to reset progress bar and message
    function resetProgress() {
        progressBar.style.width = '0';
        progressText.innerText = '0%';
        uploadMessage.innerText = '';
    }
}
