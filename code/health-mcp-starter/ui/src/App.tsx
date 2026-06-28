import { useCallback, useEffect, useMemo, useState } from "react";
import { isDemoMode, isForceDemo, subscribeDemoMode, setForceDemo } from "./demoTransport";
import {
  Briefing,
  ConditionPack,
  ConditionReport,
  DataSourcesResponse,
  Narrative,
  NextStepsResponse,
  Questions,
  Sidecar,
  SmartAnalysis,
  Timeline,
  UserContext,
  UserContextResponse,
  getJson
} from "./api";
import { Loading, ErrorBox, PartialErrorBanner } from "./components/Loading";
import { DashboardSkeleton } from "./components/DashboardSkeleton";
import { Sidebar, TabId } from "./components/Sidebar";
import { Dashboard } from "./pages/Dashboard";
import { Timeline as TimelinePage } from "./pages/Timeline";
import { Condition } from "./pages/Condition";
import { DoctorHandoff } from "./pages/DoctorHandoff";
import { MyContext } from "./pages/MyContext";
import { DataSources } from "./pages/DataSources";
import { Smart } from "./pages/Smart";
import { SidecarPage } from "./pages/Sidecar";

function DemoStatusStrip({ active, forced }: { active: boolean; forced: boolean }) {
  if (!active && !forced) {
    return (
      <div className="demo-strip live" role="status">
        <span className="demo-dot" />
        <span className="demo-label">Live API connected</span>
        <button
          type="button"
          className="demo-btn"
          onClick={() => {
            setForceDemo(true);
            window.location.reload();
          }}
        >
          Use sample data
        </button>
      </div>
    );
  }
  return (
    <div className="demo-strip sample" role="status">
      <span className="demo-dot" />
      <span className="demo-label">
        {forced ? "Sample data (locked for demo)" : "Sample data — live API not reachable"}
      </span>
      <button
        type="button"
        className="demo-btn"
        onClick={() => {
          setForceDemo(false);
          window.location.reload();
        }}
      >
        Try live API
      </button>
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState<TabId>("dashboard");
  const [briefing, setBriefing] = useState<Briefing>();
  const [timeline, setTimeline] = useState<Timeline>();
  const [sidecar, setSidecar] = useState<Sidecar>();
  const [packs, setPacks] = useState<ConditionPack[]>([]);
  const [userContext, setUserContext] = useState<UserContext>();
  const [nextStepsData, setNextStepsData] = useState<NextStepsResponse>();
  const [selectedPack, setSelectedPack] = useState("migraine");
  const [condition, setCondition] = useState<ConditionReport>();
  const [questions, setQuestions] = useState<Questions>();
  const [activeSignal, setActiveSignal] = useState("all");
  const [dataSources, setDataSources] = useState<DataSourcesResponse>();
  const [smart, setSmart] = useState<SmartAnalysis>();
  const [narrative, setNarrative] = useState<Narrative>();
  const [wave2Loading, setWave2Loading] = useState(false);
  const [error, setError] = useState<string>();
  const [fatalError, setFatalError] = useState<string>();
  const [partialErrors, setPartialErrors] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  const [demoActive, setDemoActive] = useState(isDemoMode());
  useEffect(() => subscribeDemoMode(() => setDemoActive(isDemoMode())), []);

  const refreshNextSteps = useCallback(async () => {
    const data = await getJson<NextStepsResponse>(`/api/next-steps?condition_id=${selectedPack}`);
    setNextStepsData(data);
  }, [selectedPack]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setFatalError(undefined);
      setPartialErrors([]);

      // Critical: briefing, timeline, sidecar. Optional on first paint: questions, next-steps (+ condition-packs, user-context).
      const [briefResult, timeResult, sideResult, packResult, ctxResult, qsResult, stepsResult] =
        await Promise.allSettled([
          getJson<Briefing>("/api/briefing"),
          getJson<Timeline>("/api/timeline"),
          getJson<Sidecar>("/api/sidecar"),
          getJson<{ packs: ConditionPack[] }>("/api/condition-packs"),
          getJson<UserContextResponse>("/api/user-context"),
          getJson<Questions>("/api/questions"),
          getJson<NextStepsResponse>("/api/next-steps?condition_id=migraine")
        ]);

      if (cancelled) return;

      const failed: string[] = [];
      let criticalOk = 0;

      if (briefResult.status === "fulfilled") {
        criticalOk += 1;
        setBriefing(briefResult.value);
      } else {
        failed.push("briefing");
      }

      if (timeResult.status === "fulfilled") {
        criticalOk += 1;
        setTimeline(timeResult.value);
      } else {
        failed.push("timeline");
      }

      if (sideResult.status === "fulfilled") {
        criticalOk += 1;
        setSidecar(sideResult.value);
      } else {
        failed.push("sidecar");
      }

      if (packResult.status === "fulfilled") {
        setPacks(packResult.value.packs ?? []);
        setSelectedPack((packResult.value.packs ?? [])[0]?.id ?? "migraine");
      } else {
        failed.push("condition-packs");
      }

      if (ctxResult.status === "fulfilled") {
        setUserContext(ctxResult.value.context);
      } else {
        failed.push("user-context");
      }

      if (qsResult.status === "fulfilled") {
        setQuestions(qsResult.value);
      } else {
        failed.push("questions");
      }

      if (stepsResult.status === "fulfilled") {
        setNextStepsData(stepsResult.value);
      } else {
        failed.push("next-steps");
      }

      if (criticalOk === 0) {
        setFatalError("Could not load core data (briefing, timeline, sidecar). Check that the API is running.");
      } else if (failed.length) {
        setPartialErrors(failed);
      }

      setLoading(false);
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedPack) return;
    let cancelled = false;
    async function loadCondition() {
      try {
        const data = await getJson<ConditionReport>(`/api/condition/${selectedPack}`);
        if (!cancelled) setCondition(data);
        if (!cancelled) await refreshNextSteps();
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      }
    }
    loadCondition();
    return () => {
      cancelled = true;
    };
  }, [selectedPack, refreshNextSteps]);

  useEffect(() => {
    if (tab !== "datasources" && tab !== "smart") return;
    if (tab === "datasources" && dataSources) return;
    if (tab === "smart" && smart && narrative) return;

    let cancelled = false;
    async function loadWave2() {
      setWave2Loading(true);
      try {
        if (tab === "datasources" && !dataSources) {
          const ds = await getJson<DataSourcesResponse>("/api/data-sources");
          if (!cancelled) setDataSources(ds);
        }
        if (tab === "smart" && (!smart || !narrative)) {
          const [smartData, narrativeData] = await Promise.all([
            smart ? Promise.resolve(smart) : getJson<SmartAnalysis>("/api/smart"),
            narrative ? Promise.resolve(narrative) : getJson<Narrative>("/api/narrative?locale=en")
          ]);
          if (!cancelled) {
            setSmart(smartData);
            setNarrative(narrativeData);
          }
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      } finally {
        if (!cancelled) setWave2Loading(false);
      }
    }
    loadWave2();
    return () => {
      cancelled = true;
    };
  }, [tab, dataSources, smart, narrative]);

  const disclaimer = useMemo(
    () => briefing?.disclaimer ?? timeline?.disclaimer ?? "Patterns for self-awareness — not medical diagnosis.",
    [briefing, timeline]
  );

  async function handleContextChange(ctx: UserContext) {
    setUserContext(ctx);
    await refreshNextSteps();
  }

  return (
    <div className="app-layout">
      <Sidebar
        active={tab}
        onChange={setTab}
        pendingSuggestions={nextStepsData?.pending_suggestions ?? 0}
        displayName={userContext?.profile?.display_name}
      />

      <div className="main-column">
        <DemoStatusStrip active={demoActive} forced={isForceDemo()} />
        <main>
          {loading && tab === "dashboard" && <DashboardSkeleton />}
          {loading && tab !== "dashboard" && <Loading label="Loading your data…" />}
          {fatalError && <ErrorBox message={fatalError} />}
          {error && <ErrorBox message={error} />}
          {!loading && !fatalError && partialErrors.length > 0 && (
            <PartialErrorBanner endpoints={partialErrors} />
          )}
          {!loading && !fatalError && !error && tab === "dashboard" && (
            <Dashboard
              briefing={briefing}
              sidecar={sidecar}
              context={userContext}
              nextSteps={nextStepsData?.steps ?? []}
              pendingSuggestions={nextStepsData?.pending_suggestions ?? 0}
              onNavigate={setTab}
            />
          )}
          {!loading && !fatalError && !error && tab === "context" && (
            <MyContext
              context={userContext}
              onContextChange={handleContextChange}
              onSuggestionsApplied={refreshNextSteps}
            />
          )}
          {!loading && !fatalError && !error && tab === "timeline" && (
            <TimelinePage
              entries={timeline?.entries ?? []}
              activeSignal={activeSignal}
              setActiveSignal={setActiveSignal}
            />
          )}
          {!loading && !fatalError && !error && tab === "condition" && (
            <Condition
              packs={packs}
              selected={selectedPack}
              setSelected={setSelectedPack}
              report={condition}
            />
          )}
          {!loading && !fatalError && !error && tab === "doctor" && (
            <DoctorHandoff questions={questions} context={userContext} />
          )}
          {!loading && !fatalError && !error && tab === "datasources" && (
            wave2Loading && !dataSources ? <Loading /> : <DataSources data={dataSources} />
          )}
          {!loading && !fatalError && !error && tab === "smart" && (
            wave2Loading && !smart ? <Loading /> : <Smart smart={smart} narrative={narrative} />
          )}
          {!loading && !fatalError && !error && tab === "sidecar" && (
            <SidecarPage sidecar={sidecar} />
          )}
        </main>

        <footer>
          <span>{disclaimer}</span>
          <span>Processed locally · sidecar access is logged for your review</span>
        </footer>
      </div>
    </div>
  );
}
