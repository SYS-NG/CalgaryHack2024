import React, { useState } from 'react';

const ContextChooser = ({selectedOption, setSelectedOption}) => {
//   const [selectedOption, setSelectedOption] = useState('');

  const handleOptionChange = (event) => {
    setSelectedOption(event.target.value);
  };

  return (
    <form>
      <div className="radio">
        <label>
          <input
            type="radio"
            value="preliminary evaluation"
            checked={selectedOption === "preliminary evaluation"}
            onChange={handleOptionChange}
            
          />
          Preliminary Evaluation
        </label>
      </div>
      <div className="radio">
        <label>
          <input
            type="radio"
            value="interview"
            checked={selectedOption === "interview"}
            onChange={handleOptionChange}
          />
          Interview
        </label>
      </div>
      <div className="radio">
        <label>
          <input
            type="radio"
            value="dating"
            checked={selectedOption === "dating"}
            onChange={handleOptionChange}
          />
          Dating
        </label>
      </div>
      {/* ... other form fields ... */}
    </form>
  );
}

export default ContextChooser;
