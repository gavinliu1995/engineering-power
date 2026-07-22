import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const vertexShader = /* glsl */ `
  uniform float uTime;
  uniform float uLayer;
  varying vec2 vUv;
  varying float vLift;

  void main() {
    vUv = uv;

    vec3 transformed = position;
    float longWave = sin((position.x * 0.78) + (uTime * 0.12) + (uLayer * 1.7));
    float crossWave = sin((position.y * 1.18) - (uTime * 0.09) + uLayer);
    vLift = (longWave * 0.6) + (crossWave * 0.4);
    transformed.z += vLift * 0.055;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(transformed, 1.0);
  }
`;

const fragmentShader = /* glsl */ `
  uniform float uTime;
  uniform float uLayer;
  uniform float uStart;
  uniform float uFocus;
  uniform float uEnd;
  uniform float uAmplitude;
  uniform float uFrequency;
  uniform float uPhase;
  uniform float uWidth;
  uniform float uOpacity;
  uniform vec3 uColor;
  varying vec2 vUv;
  varying float vLift;

  void main() {
    vec2 uv = vUv;
    float time = uTime * (0.11 + (uLayer * 0.012));

    float focusX = 0.64;
    float leftProgress = smoothstep(0.0, focusX, uv.x);
    float rightProgress = smoothstep(focusX, 1.0, uv.x);
    float leftCenter = mix(uStart, uFocus, leftProgress);
    float rightCenter = mix(uFocus, uEnd, rightProgress);
    float center = mix(leftCenter, rightCenter, step(focusX, uv.x));

    float mainWave = sin((uv.x * uFrequency) + uPhase + time);
    float detailWave = sin((uv.x * (uFrequency * 2.15)) - (time * 0.72) + (uPhase * 0.43));
    float waveEnvelope = 0.28 + (sin(uv.x * 3.14159265) * 0.72);
    center += ((mainWave * uAmplitude) + (detailWave * uAmplitude * 0.16)) * waveEnvelope;

    float signedDistance = uv.y - center;
    float distanceToFlow = abs(signedDistance);
    float body = 1.0 - smoothstep(uWidth * 0.08, uWidth, distanceToFlow);
    float core = 1.0 - smoothstep(0.001, 0.0055, distanceToFlow);
    float filamentOne = 1.0 - smoothstep(0.001, 0.0045, abs(signedDistance - (uWidth * 0.42)));
    float filamentTwo = 1.0 - smoothstep(0.001, 0.0035, abs(signedDistance + (uWidth * 0.58)));
    float ribbon = (body * 0.43) + (core * 0.88) + (filamentOne * 0.32) + (filamentTwo * 0.22);

    float longitudinalLight = 0.62 + (0.38 * sin((uv.x * 8.0) - (time * 2.1) + uPhase));
    float edgeLight = smoothstep(uWidth, uWidth * 0.30, distanceToFlow);
    float rightReveal = mix(0.16, 1.0, smoothstep(0.26, 0.58, uv.x));
    float edgeFade = smoothstep(0.0, 0.08, uv.x) * (1.0 - smoothstep(0.94, 1.0, uv.x));
    float verticalFade = smoothstep(0.02, 0.14, uv.y) * (1.0 - smoothstep(0.88, 0.99, uv.y));

    float alpha = ribbon * rightReveal * edgeFade * verticalFade * uOpacity;
    vec3 shadedColor = uColor * (0.72 + (longitudinalLight * 0.34) + (edgeLight * 0.18) + (vLift * 0.08));

    gl_FragColor = vec4(shadedColor, alpha);
  }
`;

type FlowRibbonProps = {
  start: number;
  focus: number;
  end: number;
  amplitude: number;
  frequency: number;
  phase: number;
  width: number;
  opacity: number;
  color: string;
  layer: number;
  z: number;
  reducedMotion: boolean;
};

function FlowRibbon({
  start,
  focus,
  end,
  amplitude,
  frequency,
  phase,
  width,
  opacity,
  color,
  layer,
  z,
  reducedMotion,
}: FlowRibbonProps) {
  const material = useRef<THREE.ShaderMaterial>(null);
  const viewport = useThree((state) => state.viewport);
  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uLayer: { value: layer },
      uStart: { value: start },
      uFocus: { value: focus },
      uEnd: { value: end },
      uAmplitude: { value: amplitude },
      uFrequency: { value: frequency },
      uPhase: { value: phase },
      uWidth: { value: width },
      uOpacity: { value: opacity },
      uColor: { value: new THREE.Color(color) },
    }),
    [amplitude, color, end, focus, frequency, layer, opacity, phase, start, width],
  );

  useFrame((state) => {
    if (!material.current || reducedMotion) return;
    material.current.uniforms.uTime.value = state.clock.elapsedTime;
  });

  return (
    <mesh position={[0, 0, z]} scale={[viewport.width, viewport.height, 1]}>
      <planeGeometry args={[1, 1, 48, 24]} />
      <shaderMaterial
        ref={material}
        fragmentShader={fragmentShader}
        vertexShader={vertexShader}
        uniforms={uniforms}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        toneMapped={false}
      />
    </mesh>
  );
}

function FlowScene({ reducedMotion }: { reducedMotion: boolean }) {
  const group = useRef<THREE.Group>(null);

  useFrame((state, delta) => {
    if (!group.current || reducedMotion) return;

    const targetX = state.pointer.y * 0.018;
    const targetY = state.pointer.x * 0.026;
    group.current.rotation.x = THREE.MathUtils.damp(group.current.rotation.x, targetX, 4.2, delta);
    group.current.rotation.y = THREE.MathUtils.damp(group.current.rotation.y, targetY, 4.2, delta);
    group.current.position.x = THREE.MathUtils.damp(group.current.position.x, state.pointer.x * 0.08, 3.6, delta);
    group.current.position.y = THREE.MathUtils.damp(group.current.position.y, state.pointer.y * 0.05, 3.6, delta);
  });

  return (
    <group ref={group}>
      <FlowRibbon start={-0.20} focus={0.46} end={0.86} amplitude={0.025} frequency={4.2} phase={4.7} width={0.22} opacity={0.17} color="#e7e9e4" layer={0.02} z={-0.4} reducedMotion={reducedMotion} />
      <FlowRibbon start={-0.10} focus={0.46} end={0.28} amplitude={0.035} frequency={5.2} phase={0.4} width={0.09} opacity={0.27} color="#d8dcd7" layer={0.1} z={-0.3} reducedMotion={reducedMotion} />
      <FlowRibbon start={-0.03} focus={0.48} end={0.44} amplitude={0.028} frequency={5.8} phase={2.3} width={0.045} opacity={0.36} color="#f2f3ee" layer={0.28} z={-0.2} reducedMotion={reducedMotion} />
      <FlowRibbon start={0.05} focus={0.49} end={0.62} amplitude={0.026} frequency={4.7} phase={4.0} width={0.03} opacity={0.58} color="#c9ff43" layer={0.46} z={-0.1} reducedMotion={reducedMotion} />
      <FlowRibbon start={0.11} focus={0.50} end={0.78} amplitude={0.032} frequency={5.4} phase={1.35} width={0.062} opacity={0.4} color="#f6f6f1" layer={0.64} z={0} reducedMotion={reducedMotion} />
      <FlowRibbon start={0.18} focus={0.51} end={0.94} amplitude={0.038} frequency={4.9} phase={3.2} width={0.032} opacity={0.37} color="#d5d8d3" layer={0.82} z={0.1} reducedMotion={reducedMotion} />
      <FlowRibbon start={0.24} focus={0.52} end={1.06} amplitude={0.044} frequency={4.5} phase={5.1} width={0.075} opacity={0.22} color="#edf0eb" layer={1.0} z={0.2} reducedMotion={reducedMotion} />
      <FlowRibbon start={0.30} focus={0.53} end={1.18} amplitude={0.036} frequency={5.7} phase={2.8} width={0.024} opacity={0.28} color="#c9cdc8" layer={1.2} z={0.28} reducedMotion={reducedMotion} />
    </group>
  );
}

export function supportsWebGL() {
  if (
    typeof window === "undefined" ||
    typeof document === "undefined" ||
    !("WebGLRenderingContext" in window)
  ) {
    return false;
  }

  try {
    const probe = document.createElement("canvas");
    const context = probe.getContext("webgl2") ?? probe.getContext("webgl");

    if (!context) return false;

    context.getExtension("WEBGL_lose_context")?.loseContext();
    return true;
  } catch {
    return false;
  }
}

export function IntelligenceFlowField({ reducedMotion = false }: { reducedMotion?: boolean }) {
  const fallback = <span className="intelligence-flow-fallback" data-testid="intelligence-flow-fallback" />;

  return (
    <div className="intelligence-flow-field" data-testid="intelligence-flow-field" aria-hidden="true">
      {supportsWebGL() ? (
        <Canvas
          camera={{ position: [0, 0, 5], fov: 42 }}
          dpr={[1, 1.5]}
          frameloop={reducedMotion ? "demand" : "always"}
          gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
          fallback={fallback}
        >
          <FlowScene reducedMotion={reducedMotion} />
        </Canvas>
      ) : fallback}
    </div>
  );
}
