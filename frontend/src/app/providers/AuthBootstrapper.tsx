import { useEffect } from "react";
import { useAuthStore } from "@/features/auth/model/store";

export default function AuthBootstrapper() {
  const setBootstrapped = useAuthStore((s) => s.setBootstrapped);

  useEffect(() => {
    useAuthStore
      .getState()
      .checkAuth()
      .finally(() => setBootstrapped());
  }, [setBootstrapped]);

  return null;
}
