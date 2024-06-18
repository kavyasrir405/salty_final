// Navbar.js
import React, { Fragment, useState, useEffect, useRef } from 'react';
import { Link, useNavigate,Navigate } from 'react-router-dom';
import { connect } from 'react-redux';
import { logout } from '../actions/auth';
import { GoPersonFill } from "react-icons/go";
import './css/navbar.css';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import IssueForm from '../containers/IssueForm';

const Navbar = ({ logout, isAuthenticated, user }) => {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [projects, setProjects] = useState([]);
    const dropdownRef = useRef(null);
    const navigate = useNavigate();
    const { projectid } = useParams();
    const [formOpen, setFormOpen] = useState(false);

    const openForm = () => {
        setFormOpen(true);
    };

    const closeForm = () => {
        setFormOpen(false);
    };

    useEffect(() => {
        if (user) {
            const fetchProjects = async () => {
                try {
                    const response = await axios.get('http://localhost:8000/djapp/project_list/', {
                        params: { email: user.email }
                    });
                    setProjects(response.data);
                } catch (error) {
                    console.error('Error fetching projects:', error);
                }
            };

            fetchProjects();
        }
    }, [user]);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsDropdownOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };

    const logoutUser = () => {
        logout();
        navigate('/'); // Programmatically navigate to the login page
    };

    const guestLinks = () => (
        <Fragment>
            <li className='nav-item'>
                <Link className='nav-link' to='/login'>
                    Login
                </Link>
            </li>
            <li className='nav-item'>
                <Link className='nav-link' to='/signup'>
                    Sign Up
                </Link>
            </li>
        </Fragment>
    );

    const authLinks = () => (
        <Fragment>
            <li className='nav-item'>
                <a className='nav-link' href='#!' onClick={logoutUser}>
                    Logout
                </a>
            </li>
        </Fragment>
    );



    const openProfile = () => {
        navigate(`/project/${projectid}/profile`);
    };

    const openMyIssues = () => {
        navigate(`/project/${projectid}/filters`);
    };

    const navtoproject = () => {
        navigate("/project");
    };

    return (
        <Fragment>
            <nav className='nav-container'>
                <ul className='nav-list'>
                    <li className='nav-item'>
                        <button className='nav-button'>Salty</button>
                    </li>
                    <li className='nav-item'>
                        <button className='nav-button' onClick={toggleDropdown}>Project</button>
                        {isDropdownOpen && (
                            <ul className='dropdown' ref={dropdownRef}>
                                {projects.map(project => (
                                    <li key={project.id}>
                                        <Link to={`/project/${project.projectid}/backlog`} className='dropdown-item'>{project.projectname}</Link>
                                    </li>
                                ))}
                            <li className='dropdown-item'onClick={navtoproject} >
                                        View Projects
                                    </li>
                                 
                            </ul>
                        )}
                    </li>
                   

                    {isAuthenticated ? authLinks() : guestLinks()}
                

                {isAuthenticated && (
                        <Fragment>
                                <button className='nav-button-create' onClick={openForm}>Create Issue</button>
                           
                        </Fragment>
                    )}

                    {formOpen && (
                        <div className="modal">
                            <div className="modal-content">
                                <span className="close" onClick={closeForm}>&times;</span>
                                <IssueForm onClose={closeForm} />
                            </div>
                        </div>
                    )}
</ul>
                {isAuthenticated && (
                    <Fragment>
                        <li className='nav-items'>
                            <button onClick={openProfile} className='person'><GoPersonFill /></button>
                        </li>
                    </Fragment>
                )}
            </nav>
        </Fragment>
    );
};

const mapStateToProps = state => ({
    isAuthenticated: state.auth.isAuthenticated,
    user: state.auth.user
});

export default connect(mapStateToProps, { logout })(Navbar);

