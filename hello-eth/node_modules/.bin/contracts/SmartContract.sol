pragma solidity >= 0.8.11 <= 0.8.11;

contract SmartContract {
    string public user_registration;
    string public access_control;
    string public permission;
       
    //call this function to register user details data to Blockchain
    function setSignup(string memory ur) public {
       user_registration = ur;	
    }
   //get register details
    function getSignup() public view returns (string memory) {
        return user_registration;
    }

    //call this function to manage access details in Blockchain
    function setAccess(string memory ac) public {
       access_control = ac;	
    }
   //get access control details
    function getAccess() public view returns (string memory) {
        return access_control;
    }

    //call this function to manage permission details in Blockchain
    function setPermission(string memory per) public {
       permission = per;	
    }
   //get permission details
    function getPermission() public view returns (string memory) {
        return permission;
    }

   constructor() public {
        user_registration="";
	access_control="";
	permission="";
    }
}