import React, { useState } from 'react';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserPlus } from '@fortawesome/free-solid-svg-icons';
import './css/add_team.css';
import loadingGif from './css/loadingGif.gif'; // Adjust the path accordingly


const AddTeamMembers = ({ projectid }) => {
    const [email, setEmail] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const sendInvitation = async () => {
        setIsLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/djapp/generate_invitation_token/', { email: email, projectid: projectid });
            console.log("pressed submit email", response.data);  // or do something else upon success
            setShowForm(false); // Close the form upon successful submission
        } catch (error) {
            console.error('Error sending invitation:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            sendInvitation();
        }
    };

    return (
        <div>
            <FontAwesomeIcon
                icon={faUserPlus}
                className="add-team-icon"
                onClick={() => setShowForm(true)}
            />
            {showForm && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <span className="close" onClick={() => setShowForm(false)}>&times;</span>
                        <h2>Add Team Member</h2>
                        <div className="add-team-form">
                            <input
                                className='add-team-form-inputs'
                                type="email"
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                placeholder="Enter email"
                                onKeyDown={handleKeyDown}
                            />
                            <button onClick={sendInvitation} disabled={isLoading}>
                                {isLoading ? <img src={loadingGif} alt="Loading..." className="loading-gif" /> : 'Send Invitation'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AddTeamMembers;
