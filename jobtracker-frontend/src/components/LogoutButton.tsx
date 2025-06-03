import { logout } from "@services/api";
import { useNavigate } from "react-router-dom";

function NavBar() {
  const navigate = useNavigate();
  async function handleLogout() {
    await logout();
    navigate("/login");
  }
  return <button onClick={handleLogout}>Logout</button>;
}