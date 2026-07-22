import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";

vi.mock("@react-three/fiber", () => ({
  Canvas: ({ frameloop, fallback }: { frameloop: string; fallback: React.ReactNode }) => (
    <div
      data-testid="mock-r3f-canvas"
      data-frameloop={frameloop}
      data-has-fallback={Boolean(fallback)}
    />
  ),
  useFrame: vi.fn(),
  useThree: vi.fn(),
}));

import { IntelligenceFlowField } from "./IntelligenceFlowField";

const originalWebGLDescriptor = Object.getOwnPropertyDescriptor(window, "WebGLRenderingContext");

function enableWebGLProbe() {
  Object.defineProperty(window, "WebGLRenderingContext", {
    configurable: true,
    value: function WebGLRenderingContext() {},
  });

  const loseContext = vi.fn();
  const getContext = vi
    .spyOn(HTMLCanvasElement.prototype, "getContext")
    .mockImplementation(() => ({ getExtension: () => ({ loseContext }) }) as unknown as WebGLRenderingContext);

  return { getContext, loseContext };
}

afterEach(() => {
  vi.restoreAllMocks();

  if (originalWebGLDescriptor) {
    Object.defineProperty(window, "WebGLRenderingContext", originalWebGLDescriptor);
  } else {
    Reflect.deleteProperty(window, "WebGLRenderingContext");
  }
});

describe("IntelligenceFlowField", () => {
  test("renders a quiet fallback when WebGL is unavailable", () => {
    render(<IntelligenceFlowField />);

    expect(screen.getByTestId("intelligence-flow-fallback")).toBeInTheDocument();
    expect(screen.queryByTestId("mock-r3f-canvas")).not.toBeInTheDocument();
  });

  test("uses demand rendering when reduced motion is requested", () => {
    const { getContext, loseContext } = enableWebGLProbe();

    render(<IntelligenceFlowField reducedMotion />);

    expect(screen.getByTestId("mock-r3f-canvas")).toHaveAttribute("data-frameloop", "demand");
    expect(screen.getByTestId("mock-r3f-canvas")).toHaveAttribute("data-has-fallback", "true");
    expect(getContext).toHaveBeenCalledWith("webgl2");
    expect(loseContext).toHaveBeenCalledOnce();
  });

  test("keeps the live field animating when reduced motion is not requested", () => {
    enableWebGLProbe();

    render(<IntelligenceFlowField />);

    expect(screen.getByTestId("mock-r3f-canvas")).toHaveAttribute("data-frameloop", "always");
  });
});
