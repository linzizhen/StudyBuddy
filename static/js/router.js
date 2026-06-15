/**
 * StudyPal 路由系统 v2.3
 * 支持 Hash + 直接 URL 访问，基于 pushState 无刷新导航
 * 优化：移除 50ms 轮询，改为 app-ready 事件驱动
 */

class Router {
    constructor() {
        this.routes = new Map();
        this.currentPage = null;
        this.currentParams = [];
        this._pendingRoute = null; // 缓存 App 未就绪时的路由请求
        this._init();
    }

    register(name, handler) {
        this.routes.set(name, handler);
    }

    _init() {
        window.addEventListener('popstate', () => this._handleRoute());

        window.addEventListener('app-ready', () => {
            // App 就绪后，如果有 pending 路由则执行
            if (this._pendingRoute) {
                const { page, params } = this._pendingRoute;
                this._pendingRoute = null;
                this._handleRoute();
            } else {
                this._handleRoute();
            }
        });

        // App-ready 监听器如果已错过，在 load 时检查 App 状态
        window.addEventListener('load', () => {
            if (window.App && window.App._routerReady) {
                this._handleRoute();
            }
        });
    }

    _handleRoute() {
        let page = window.location.pathname.replace(/^\//, '').split('/')[0];
        if (!page || page === 'app' || page === 'index.html') page = 'home';

        const hash = window.location.hash.slice(1);
        if (hash) {
            const hashPage = hash.split('/')[0];
            if (this.routes.has(hashPage)) {
                page = hashPage;
            }
        }

        const params = [];
        if (hash) {
            const parts = hash.split('/');
            if (parts.length > 1) params.push(...parts.slice(1));
        }

        if (this.routes.has(page)) {
            this.navigate(page, params, true);
        } else {
            this.navigate('home', [], true);
        }
    }

    navigate(page, params = [], fromHistory = false) {
        if (!this.routes.has(page)) return;

        if (this.currentPage === page && JSON.stringify(this.currentParams) === JSON.stringify(params)) {
            return;
        }

        if (this.currentPage && this.routes.get(this.currentPage)?.unmount) {
            this.routes.get(this.currentPage).unmount();
        }

        this.currentPage = page;
        this.currentParams = params;

        const handler = this.routes.get(page);
        handler.mount(params);
        this._updateNavigation(page);

        if (!fromHistory) {
            const newHash = params.length > 0 ? `#${page}/${params.join('/')}` : `#${page}`;
            window.history.pushState({ page, params }, '', newHash);
        }
    }

    _updateNavigation(page) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });
        if (window.State) {
            State.set('ui.currentPage', page);
        }
    }

    getCurrentPage() {
        return this.currentPage;
    }

    getParams() {
        return this.currentParams;
    }

    goHome() {
        this.navigate('home');
    }

    refresh() {
        if (this.currentPage) {
            this.navigate(this.currentPage, this.currentParams, true);
        }
    }
}

const router = new Router();
window.Router = Router;
window.router = router;
