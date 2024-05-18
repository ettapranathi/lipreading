import React from 'react'
import { Link } from 'react-router-dom';
const VideoProcessor = () => {
  return (
    <div className='output'>
      <h2>Output</h2>
      {/* Display your output sentences and accuracy here */}
      <p>Sentences: {/* sentences from state */}</p>
      <p>Accuracy: {/* accuracy from state */}</p>
      <Link to="/">Go back to input page</Link>
    </div>
  )
}

export default VideoProcessor
