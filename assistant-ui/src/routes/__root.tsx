import { createRootRoute, Outlet } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";

export const Route = createRootRoute({
  component: () => (
    <>
      <div className="w-full h-full flex flex-col items-center">
        <Outlet />
      </div>
      <TanStackRouterDevtools />
    </>
  ),
});
