import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./app/index";
import "./shared/styles/globals.css";

import { setAuthApi } from "@/features/auth/api/api";
import { authApiMock } from "@/features/auth/api/api-mock";
import { setProfileApi } from "@/features/profile/api/profile-api";
import { profileApiMock } from "@/features/profile/api/profile-api-mock";

setProfileApi(profileApiMock);
setAuthApi(authApiMock);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
