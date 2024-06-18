import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import './css/DIF.css';
import CustomDropdown from './CustomDropdown';

const DisplayIssueFilters = ({ data, user }) => {
  const [issue, setIssue] = useState(data);
  const [isEditing, setIsEditing] = useState(false);
  const [assigneeOptions, setAssigneeOptions] = useState([]);
  const [sprintOptions, setSprintOptions] = useState([]);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(issue.projectId_id);
  const [files, setFiles] = useState([]);
  const [epics, setEpics] = useState([]);

  useEffect(() => {
    setIssue(data);
    { console.log(issue) }
  }, [data]);

  useEffect(() => {
    const fetchTeamMembersAndSprints = async () => {
      try {
        const teamMembersResponse = await axios.get(`http://localhost:8000/djapp/get_team_members/?projectid=${selectedProject}`);
        setAssigneeOptions(teamMembersResponse.data.team_members);
        console.log(teamMembersResponse);

        const sprintsResponse = await axios.get(`http://localhost:8000/djapp/get_sprints/?projectid=${selectedProject}`);
        setSprintOptions(sprintsResponse.data.sprint_in_project);
      } catch (error) {
        console.error('Error fetching team members and sprints:', error);
      }
    };

    if (selectedProject) {
      fetchTeamMembersAndSprints();
    }
  }, [selectedProject]);

  useEffect(() => {
    const fetchEpics = async () => {
      try {
        if (!selectedProject) return;
        const response = await axios.get(`http://localhost:8000/djapp/get_epics/?projectid=${selectedProject}`);
        setEpics(response.data.epics_in_project);
        console.log(response)
      } catch (error) {
        console.error('Error fetching epics:', error);
      }
    };

    fetchEpics();
  }, [selectedProject]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'assignee') {
      setIssue(prevIssue => ({
        ...prevIssue,
        [name]: value,
        assigned_by: user.email
      }));
    } else if (name === 'file_field') {
      setFiles([...files, ...e.target.files]);
    } else {
      setIssue(prevIssue => ({
        ...prevIssue,
        [name]: value
      }));
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = async () => {
    try {
      await axios.post(`http://localhost:8000/djapp/update_issue/`, issue);
      setIsEditing(false);
    } catch (error) {
      console.error("There was an error updating the issue!", error);
    }
  };

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/djapp/project_list/?email=${user.email}`);
        setProjects(response.data || []);
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    };

    fetchProjects();
  }, [user.email]);

  return (
    <div className='display-issue-main-container'>
      {issue ? (
        <div className="display-issue-card">
          <h1 className="display-issue-title">{issue.IssueName || '----'}</h1>
          {/* <p>
            <strong>Assigned by:</strong> {issue.assigned_by || '----'}
          </p> */}
          <p>
            <strong>Type:</strong>
            {isEditing ? (
              <select className="display-issue-select" name="IssueType" value={issue.IssueType} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="Story">Story</option>
                <option value="Task">Task</option>
                <option value="Bug">Bug</option>
                <option value="Epic">Epic</option>
              </select>
            ) : (
              issue.IssueType || '----'
            )}
          </p>
          <p>
            <strong>Description:</strong>
            {isEditing ? (
              <textarea className="display-issue-textarea" name="description" value={issue.description} onChange={handleChange} />
            ) : (
              issue.description || '----'
            )}
          </p>
          <p>
            <strong>Status:</strong>
            {isEditing ? (
              <select className="display-issue-select" name="status" value={issue.status} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="to_do">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
              </select>
            ) : (
              issue.status || '----'
            )}
          </p>
          <p>
            <strong>Assigned to:</strong>
            {isEditing ? (
              <>
                <CustomDropdown
                  options={assigneeOptions}
                  value={issue.assignee}
                  onChange={handleChange} />
              </>
            ) : (
              issue.assignee || '----'
            )}
          </p>
          <p>
            <strong>Epic:</strong>
            {isEditing ? (
              <div>
                <select value={issue.assigned_epic_id} className="display-issue-input" name="assigned_epic" onChange={handleChange}>
                  <option value=''>Select...</option>
                  {epics.map((epic) => (
                    <option key={epic.Epic_Id} value={epic.Epic_Id}>
                      {epic.EpicName}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              issue.assigned_epic || '----'
            )}
          </p>
          <p>
            <strong>Sprint:</strong>
            {isEditing ? (
              <select className="display-issue-select" name="sprint_id" value={issue.sprint_id} onChange={handleChange}>
                <option value="">Select...</option>
                {sprintOptions.map(sprint => (
                  <option key={sprint.sprint} value={sprint.sprint}>
                    {sprint.sprint}
                  </option>
                ))}
              </select>
            ) : (
              issue.sprint_id || '----'
            )}
          </p>
          <p>
            <strong>Project ID:</strong>
            {isEditing ? (
              <div>
                <select className="display-issue-select" value={selectedProject} onChange={(e) => setSelectedProject(e.target.value)}>
                  <option value="">Select...</option>
                  {projects.map((project) => (
                    <option key={project.projectid} value={project.projectid}>
                      {project.projectname}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              issue.projectId_id || '----'
            )}
          </p>
          <p>
            <strong>Story Points:</strong>
            {isEditing ? (
              <div className="display-issue-slider-container">
                <input
                  type="range"
                  min="1"
                  max="3"
                  name="StoryPoint"
                  value={issue.StoryPoint}
                  onChange={handleChange}
                  className="display-issue-slider"
                />
              </div>
            ) : (
              issue.StoryPoint || '----'
            )}
          </p>
          <p>
            <strong>Priority:</strong>
            {isEditing ? (
              <select className="display-issue-select" name="priority" value={issue.Priority} onChange={handleChange}>
                <option value="">Select...</option>
                <option value="Highest">Highest</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
                <option value="Lowest">Lowest</option>
              </select>
            ) : (
              issue.priority || '----'
            )}
          </p>
          <p>
            <strong>Files:</strong>
            {isEditing ? (
              <input className="display-issue-file-input" type="file" name="file_field" onChange={handleChange} multiple />
            ) : (
              (issue.files && issue.files.length > 0) ? (
                issue.files.map(file => (
                  <a href={`/path/to/files/${file.file_field}`} key={file.id} className="display-issue-file-link">{file.file_field}</a>
                ))
              ) : (
                <span>----</span>
              )
            )}
          </p>
          {isEditing ? (
            <button className="display-issue-button" onClick={handleSave}>Save</button>
          ) : (
            <button className="display-issue-button" onClick={handleEdit}>Edit</button>
          )}
        </div>
      ) : (
        <p>No issues found</p>
      )}
    </div>
  );
};

const mapStateToProps = state => ({
  user: state.auth.user // Assuming the user information is stored in the 'auth' slice of the Redux state
});

export default connect(mapStateToProps)(DisplayIssueFilters);


