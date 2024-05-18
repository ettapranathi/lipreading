import React, { useState } from 'react';
// import ReactPlayer from 'react-player';

const VideoInputComponent = ({ onProcess }) => {
  const [video, setVideo] = useState(null);
  const [error, setError] = useState('');
  const [videoURL,setvideoURL]=useState(null);
  const handleVideoChange = (event) => {
    const selectedVideo = event.target.files[0];
    if (selectedVideo) {
      if (selectedVideo.type.startsWith('video/')) {
        console.log('video');
        setVideo(selectedVideo);
        setError('');
        const objectURL = URL.createObjectURL(selectedVideo);
        setvideoURL(objectURL);
        console.log(objectURL)
      } else {
        setVideo(null);
        setError('Invalid file type. Please select a video file.');
      }
    } else {
      setVideo(null);
      setError('No file selected. Please select a video file.');
    }
  };

  const handleProcessing = () => {
    if (video) { // Only process if video exists
      onProcess(video);
    } else {
      setError('No video file selected. Please select a video file.');
    }
  };

  return (
    
    <div>
      <h2>Video Input</h2>
      <input type="file" accept="video/mpg" onChange={handleVideoChange} />
      {/* {videoURL && (
        <div>
          <video controls width="500">
            <source src={video} type="video/mpeg" />
            Your browser does not support the video tag.
          </video>
        </div>
      )} */}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button onClick={handleProcessing}>Process Video</button>
    </div>
  );
};
export default VideoInputComponent;