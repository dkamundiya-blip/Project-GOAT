/**
 * Project GOAT v1.0 — Replay Hooks Preparation
 * Step 1.6 Institutional TradingView Charting Engine
 *
 * Exposes interfaces and state preparation hooks for future historical market replay mode.
 */

export interface ReplayState {
  isReplayActive: boolean;
  replaySpeed: number; // 1x, 2x, 5x, 10x, 50x
  replayTimestamp: number | null;
  startTimestamp: number | null;
  endTimestamp: number | null;
  isPlaying: boolean;
}

export interface ReplayController {
  startReplay: (startTimestamp: number, endTimestamp: number) => void;
  stopReplay: () => void;
  play: () => void;
  pause: () => void;
  stepForward: () => void;
  setSpeed: (speed: number) => void;
  seekTo: (timestamp: number) => void;
}

export class ReplayHooks {
  static createDefaultReplayState(): ReplayState {
    return {
      isReplayActive: false,
      replaySpeed: 1,
      replayTimestamp: null,
      startTimestamp: null,
      endTimestamp: null,
      isPlaying: false,
    };
  }

  static createMockReplayController(onStateChange?: (state: ReplayState) => void): ReplayController {
    let state = this.createDefaultReplayState();

    const notify = () => {
      if (onStateChange) onStateChange({ ...state });
    };

    return {
      startReplay: (start, end) => {
        state.isReplayActive = true;
        state.startTimestamp = start;
        state.endTimestamp = end;
        state.replayTimestamp = start;
        state.isPlaying = false;
        notify();
      },
      stopReplay: () => {
        state = this.createDefaultReplayState();
        notify();
      },
      play: () => {
        if (state.isReplayActive) {
          state.isPlaying = true;
          notify();
        }
      },
      pause: () => {
        if (state.isReplayActive) {
          state.isPlaying = false;
          notify();
        }
      },
      stepForward: () => {
        if (state.isReplayActive && state.replayTimestamp !== null) {
          state.replayTimestamp += 60000;
          notify();
        }
      },
      setSpeed: (speed) => {
        state.replaySpeed = speed;
        notify();
      },
      seekTo: (ts) => {
        if (state.isReplayActive) {
          state.replayTimestamp = ts;
          notify();
        }
      },
    };
  }
}
