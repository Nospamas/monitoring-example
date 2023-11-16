import Semaphore from '../../../semaphore-api.mjs'

(async () => {
    Semaphore.startTask(Semaphore.projects.HomeNetwork, Semaphore.tasks.DeployMonitoringServer)
})();