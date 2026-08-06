/**
 * Project GOAT v1.0 — Official TradingView Charting Library Asset Loader & Detector
 * Step 1.6 Institutional TradingView Charting Engine
 */

export class TradingViewLoader {
  private static libraryScriptUrl = '/charting_library/charting_library.min.js';

  static isOfficialLibraryLoaded(): boolean {
    return typeof (window as any).TradingView !== 'undefined' && typeof (window as any).TradingView.widget === 'function';
  }

  static async loadOfficialLibrary(): Promise<boolean> {
    if (this.isOfficialLibraryLoaded()) {
      return true;
    }

    return new Promise((resolve) => {
      const script = document.createElement('script');
      script.src = this.libraryScriptUrl;
      script.type = 'text/javascript';
      script.async = true;

      script.onload = () => {
        resolve(this.isOfficialLibraryLoaded());
      };

      script.onerror = () => {
        resolve(false);
      };

      document.head.appendChild(script);
    });
  }
}
