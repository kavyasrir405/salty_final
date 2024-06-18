import { GiSprint } from "react-icons/gi";

import Backlog from './Backlog';
import React, { useState , useEffect} from 'react';
import { useLocation, useParams } from 'react-router-dom';
import axios from 'axios';
import Sprint from './Sprint';
import IssueForm from './IssueForm';
import { RiArrowDropDownLine } from "react-icons/ri";
import { RiArrowDropUpLine } from "react-icons/ri";
import Add_team_members from './Add_team_members';
import  "./css/DisplayBacklog.css";
import Sidebar from "../components/Sidebar"
import ProjectPage from "./ProjectPage";


export default function DisplayBacklog() {
   
    const {projectid}=useParams()
    const [sprints, setSprints] = useState([]);
    const [issues, setissues] = useState([]);
    const [formOpen, setFormOpen] = useState(false);
    const [sprintCount, setSprintCount] = useState(0); // Initially no sprints
    const [sprintCreated, setSprintCreated] = useState(false);
    const [deletedSprint,setdeletedSprint]=useState(false)
    const [backlogsListOpen, setBacklogsListOpen] = useState(true);
    const[isSprintDeleted,setisSprintDeleted]=useState(false)
    const[issueDragged,setissueDragged]=useState(false)
    const [issueStatusChanged, setIssueStatusChanged] = useState(false);
   

    const openForm = () => {
      setFormOpen(true);
    };
 
    // Function to close form<button onClick={openForm}>Create</button>
    const closeForm = () => {
      setFormOpen(false);
    };
    const fetchData = async () => {
      try {
        console.log("hellooooo inside fetchdattttttttta")
        const response = await axios.get("http://localhost:8000/djapp/countsprints/", {
          params: { projectId: projectid }
        });
        const data = response.data;
        console.log("inside before useEffect", isSprintDeleted);
        setisSprintDeleted(false);
        console.log("inside useEffect", isSprintDeleted);
        setSprints(data.sprints); // Assign array of sprint objects to state variable
        console.log("datadddd", data.sprints);
        console.log("sprintss", sprints);
        if (data.sprints.length > 0) {
          const lastSprint = data.sprints[data.sprints.length - 1];
          const lastSprintNumber = parseInt(lastSprint.sprint.match(/Sprint (\d+)/)[1]);
          setSprintCount(lastSprintNumber);
        } else {
         
          setSprintCount(0);
         
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
   
    useEffect(() => {
      fetchData();
    }, [deletedSprint, sprintCount, isSprintDeleted]);
   
    useEffect(() => {
        const fetchIssues = async () => {
         
          try {
            const response = await axios.get("http://localhost:8000/djapp/issues/",
            {
              params: { projectId: projectid}
          },
            );
           
            setissues(response.data)
            setIssueStatusChanged(false)
            console.log("issuessswithoutttsprinttttt",response.data)
            console.log(issues)
          } catch (error) {
            console.error("Error fetching data:", error);
          }
        };fetchIssues();
      }, [projectid,issueStatusChanged]);
   
      const handleCreateSprint = async () => {
        try {
          const sprintName = `Sprint ${sprintCount + 1}-${projectid.substring(0, 4)}`;
         
          await axios.post('http://localhost:8000/djapp/update_sprintName/', { sprintName:sprintName,projectid:projectid });
          setSprintCount(prevCount => prevCount + 1);
          setSprintCreated(true);
      } catch (error) {
          console.error("Error creating sprint:", error);
      }
    };
    const toggleBacklogsList = () => {
      setBacklogsListOpen(!backlogsListOpen);
    };
  return (
    <><Sidebar/>
   
    <div className="Displaybacklog-main">
   
   
    <div className='mainContainer'>
       
    <div className='firstDiv'>
      <h1>Backlog </h1>
     <Add_team_members projectid={projectid}/>

      {/* <button onClick={openForm} className='createClass'>Create</button> */}
      {formOpen && (
          <div className="modal">
            <div className="modal-content">
              <span className="close" onClick={closeForm}>&times;</span>
              <IssueForm onClose={closeForm} />
            </div>
          </div>
        )}
    </div>
    <div className="sprints-maindiv">
    <div className="sprints-empty">
    {sprintCount === 0 &&<><div  className="EmptyS"><p className="emptySprintDiv">Click on "Create Sprint" to create your first sprint</p><div className="sprint-icon"><GiSprint /></div></div>
    <button className='createSprintwhenEmpty' onClick={handleCreateSprint}>Create Sprint</button> </>
   

    }
    {sprints.filter(sprint => sprint.status !== 'completed').map((sprint, index) => (
    <Sprint key={index} sprint={sprint}  fetchData={fetchData} onSprintDelete={setisSprintDeleted} setissueDragged={setissueDragged}  onissueTypeChange={setIssueStatusChanged} />
))}
    </div>
    </div>
   
        {sprintCount !== 0  &&
    <button className='createSprint' onClick={handleCreateSprint}>Create Sprint</button>


    }
   
       
        <div className='backlogsList'>
          <div className='firstDiv'>
          <button className="react-icon" onClick={toggleBacklogsList} >
          {backlogsListOpen ? <RiArrowDropUpLine  /> : <RiArrowDropDownLine />}
        </button>
          <h3 >Backlogs</h3>
       
     
       </div>
       
       {backlogsListOpen && <Backlog issuesList={issues} sprint_name={null}  onSprintDelete={setisSprintDeleted}  onissueTypeChange={setIssueStatusChanged}/>}
     
      </div>
     
    </div>
    </div> </>
  )
}

