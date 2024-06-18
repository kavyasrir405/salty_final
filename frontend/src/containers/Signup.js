import React, { useState } from 'react';
import { Link, Navigate,useNavigate, useLocation} from 'react-router-dom';
import { connect } from 'react-redux';
import { signup } from '../actions/auth';
import axios from 'axios';
import './css/Signup.css';  // Import the CSS file

const Signup = ({ signup, isAuthenticated }) => {
    const [accountCreated, setAccountCreated] = useState(false);
    const [formData, setFormData] = useState({
        first_name: '',
        last_name:'',
        email: '',
        password: '',
        re_password: ''
    });
    const navigate = useNavigate();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
  
  const projectId = searchParams.get('projectid');
    const { first_name, last_name, email, password, re_password } = formData;

    const onChange = e => setFormData({ ...formData, [e.target.name]: e.target.value });

    const onSubmit = e => {
        e.preventDefault();

        if (password === re_password) {
            signup(first_name, last_name, email, password, re_password);
            setAccountCreated(true);
        }
    };

    const continueWithGoogle = async () => {
        try {
            const res = await axios.get(`${process.env.REACT_APP_API_URL}/auth/o/google-oauth2/?redirect_uri=http://localhost:8000`);

            window.location.replace(res.data.authorization_url);
        } catch (err) {
            // Handle the error
        }
    };

    if (isAuthenticated) {
        return <Navigate to='/' />
    }
    if (accountCreated) {
        return navigate(`/login?projectid=${projectId}`); 
    }

    return (
        <div className='signup-page'>
            <div className='signup-container'>
                <h1 className='signup-heading'>Sign Up</h1>
                <p className='signup-subheading'>Create your Account</p>
                <form onSubmit={e => onSubmit(e)}>
                    <div className='signup-form-group'>
                        <input
                            className='signup-form-control'
                            type='text'
                            placeholder='First Name*'
                            name='first_name'
                            value={first_name}
                            onChange={e => onChange(e)}
                            required
                        />
                    </div>
                    <div className='signup-form-group'>
                        <input
                            className='signup-form-control'
                            type='text'
                            placeholder='Last Name*'
                            name='last_name'
                            value={last_name}
                            onChange={e => onChange(e)}
                            required
                        />
                    </div>
                    <div className='signup-form-group'>
                        <input
                            className='signup-form-control'
                            type='email'
                            placeholder='Email*'
                            name='email'
                            value={email}
                            onChange={e => onChange(e)}
                            required
                        />
                    </div>
                    <div className='signup-form-group'>
                        <input
                            className='signup-form-control'
                            type='password'
                            placeholder='Password*'
                            name='password'
                            value={password}
                            onChange={e => onChange(e)}
                            minLength='6'
                            required
                        />
                    </div>
                    <div className='signup-form-group'>
                        <input
                            className='signup-form-control'
                            type='password'
                            placeholder='Confirm Password*'
                            name='re_password'
                            value={re_password}
                            onChange={e => onChange(e)}
                            minLength='6'
                            required
                        />
                    </div>
                    <button className='signup-btn signup-btn-primary' type='submit'>Register</button>
                </form>
               
                <p className='signup-text mt-3'>
                    Already have an account? <Link to='/login' className='signup-link'>Sign In</Link>
                </p>
            </div>
        </div>
    );
};

const mapStateToProps = state => ({
    isAuthenticated: state.auth.isAuthenticated
});

export default connect(mapStateToProps, { signup })(Signup);

