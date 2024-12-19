//on connection get all available offers and call createOfferEls
socket.on('availableOffers',offers=>{
    console.log(offers)
    createOfferEls(offers)
})

//someone just made a new offer and we're already here - call createOfferEls
socket.on('newOfferAwaiting',offers=>{
    createOfferEls(offers)
})

socket.on('answerResponse',offerObj=>{
    console.log(offerObj)
    addAnswer(offerObj)
})

socket.on('receivedIceCandidateFromServer',iceCandidate=>{
    addNewIceCandidate(iceCandidate)
    console.log(iceCandidate)
})

function createOfferEls(offers){
    //make green answer button for this new offer
    const answerEl = document.querySelector('#answer');
    offers.forEach(o=>{
        console.log(o);
        const newOfferEl = document.createElement('div');
        newOfferEl.innerHTML = `<button class="btn btn-success col-1">Answer ${o.offererUserName}</button>`
        newOfferEl.addEventListener('click',()=>answerOffer(o))
        answerEl.appendChild(newOfferEl);
    })
}

// Assuming you have a function to capture frames from the video element
const captureFrame = () => {
    const canvas = document.createElement('canvas');
    canvas.width = localVideoEl.videoWidth;
    canvas.height = localVideoEl.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(localVideoEl, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
};

const sendProcessedFrameToPeer = (processedFrame) => {
    // Assuming you have a socket connection established
    socket.emit('processedFrame', { frame: processedFrame });
};

// Function to send the frame to the Flask server for processing
const sendFrameToServer = async (frameData) => {
    try {
        console.log('Sending frame data:', frameData); // Log the frame data
        const response = await fetch('http://localhost:5000/video_frame', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ frame: frameData }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log(result.message); // Log the success message
    } catch (error) {
        console.error('Error sending frame to server:', error);
    }
};

// Call this function periodically or on a specific event
const processAndSendFrame = () => {
    const frameData = captureFrame();
    sendFrameToServer(frameData);
};

// Example: Call processAndSendFrame every second
setInterval(processAndSendFrame, 1000);

const displayProcessedFrame = (processedFrame) => {
    const processedVideoEl = document.querySelector('#processed-video'); // Assuming you have an <img> or <canvas> element
    processedVideoEl.src = processedFrame; // Set the src of the <img> to the processed frame
};

// HTML Example
// <img id="processed-video" alt="Processed Video Frame" />