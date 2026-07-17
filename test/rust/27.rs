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
