// test async, await and dyn
trait Task {
    async fn run(&self);
}

async fn execute(task: &dyn Task) {
    let future = async move {
        task.run()
    };

    future.await;
}

async fn async_main(cfg: config::ServerConfig, debug: bool) -> anyhow::Result<()> {
    // ...
    let state = state::AppState::new(cfg.clone(), logger.clone()).await;
    let app = routes::build_router(state);

    let listener = tokio::net::TcpListener::bind(&cfg.bind).await?;

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await?;
}