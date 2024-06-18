import React from 'react';
import { AiFillCaretRight } from "react-icons/ai";
import './css/Hpage.css'
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { connect } from 'react-redux';

const Home = ({ isAuthenticated }) => {
  const navigate = useNavigate();

  const handleLoginButton = () => {
    navigate('/login');
  };

  const moveToProjects = () => {
    navigate('/projects');
  }

  return (
    <div className="container">
      {!isAuthenticated ? (
        <div className="content">
          <h3 className='welcome-header'>WELCOME TO</h3>
          <div className='salty-header'>
          <h1>S</h1>
          <h1>A</h1>
          <h1>L</h1>
          <h1>T</h1>
          <h1>Y</h1>
          </div>

          <div className="button-div">
            <button type="button" className="continue-to-login" onClick={handleLoginButton}>
              <AiFillCaretRight className="apple-icon" />
              Continue to Use
            </button>
          </div>
        </div>
      ) : (
        // <button onClick={moveToProjects} className="project-button">
        //   Move to Projects
        // </button>
         <Navigate to={`/project`} ></Navigate>
      )}
    </div>
  );
};

const mapStateToProps = state => ({
  isAuthenticated: state.auth.isAuthenticated // Assuming the user information is stored in the 'auth' slice of the Redux state
});

export default connect(mapStateToProps)(Home);

