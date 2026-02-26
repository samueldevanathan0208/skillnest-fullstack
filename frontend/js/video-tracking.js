/**
 * Unified Video Tracking Logic for LMS
 * Requirements:
 * - Track duration using player.getDuration()
 * - Track watched time using player.getCurrentTime()
 * - Unlock Next button at 50% duration
 * - Anti-cheat: pull back if seeking ahead of maxWatchedTime
 * - Detailed 1s debug logging
 * - Heartbeat to backend every 5s
 */

class VideoTracker {
    constructor(config) {
        this.courseId = config.courseId;
        this.currentIndex = config.currentIndex || 0;
        this.nextBtnId = config.nextBtnId || 'nextBtn';
        this.player = null;
        this.maxWatchedTime = 0;
        this.totalDuration = 0;
        this.requiredWatchTime = 0;
        this.watchInterval = null;
        this.heartbeatInterval = null;
        this.isUnlocked = false;
        this.hasResumed = false;
        this.videos = config.videos;
        this.onProgressUpdate = config.onProgressUpdate || (() => { });
        this.onUnlock = config.onUnlock || (() => { });

        console.log(`[VideoTracker] Initialized for course: ${this.courseId}`);
    }

    async init(index) {
        this.currentIndex = index;
        const video = this.videos[index];
        const videoId = video.src.split("/embed/")[1]?.split("?")[0];

        // Reset state
        this.maxWatchedTime = 0;
        this.totalDuration = 0;
        this.requiredWatchTime = 0;
        this.isUnlocked = false;
        this.hasResumed = false;

        if (this.watchInterval) clearInterval(this.watchInterval);
        if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);

        // Fetch saved progress
        const savedState = await this.fetchVideoState(index);
        if (savedState && savedState.last_watched_time > 0) {
            this.maxWatchedTime = savedState.last_watched_time;
            console.log(`[VideoTracker] Resuming at ${this.maxWatchedTime}s`);
        }

        this.setupPlayer(videoId);
    }

    setupPlayer(videoId) {
        if (this.player && typeof this.player.loadVideoById === 'function') {
            this.player.loadVideoById(videoId);
        } else {
            this.player = new YT.Player('ytVideo', {
                videoId: videoId,
                playerVars: {
                    'autoplay': 1,
                    'modestbranding': 1,
                    'rel': 0,
                    'enablejsapi': 1,
                    'origin': window.location.origin
                },
                events: {
                    onReady: () => this.onPlayerReady(),
                    onStateChange: (event) => {
                        if (event.data === YT.PlayerState.PLAYING) {
                            this.startTracking();
                        } else {
                            this.stopTracking();
                        }
                    }
                }
            });
        }
    }

    onPlayerReady() {
        if (this.maxWatchedTime > 0 && !this.hasResumed) {
            this.player.seekTo(this.maxWatchedTime);
            this.hasResumed = true;
        }
    }

    startTracking() {
        if (this.watchInterval) clearInterval(this.watchInterval);

        this.watchInterval = setInterval(() => {
            if (!this.player || typeof this.player.getDuration !== 'function') return;

            const duration = this.player.getDuration();
            if (duration <= 0) return; // Wait for duration to be available

            this.totalDuration = duration;
            this.requiredWatchTime = duration * 0.5;

            const currentTime = this.player.getCurrentTime();

            // Anti-cheat: Track max watched time
            if (currentTime > this.maxWatchedTime && currentTime <= this.maxWatchedTime + 2) {
                this.maxWatchedTime = currentTime;
            }

            // Prevent skipping ahead
            if (currentTime > this.maxWatchedTime + 5) {
                console.warn("[VideoTracker] Skip detected. Pulling back to:", this.maxWatchedTime);
                this.player.seekTo(this.maxWatchedTime);
            }

            const percentage = (this.maxWatchedTime / this.totalDuration) * 100;
            const unlockCondition = this.maxWatchedTime >= this.requiredWatchTime;

            // Structured Debug Log (Requirement #4)
            console.log({
                duration: this.totalDuration,
                currentTime: currentTime,
                maxWatchedTime: this.maxWatchedTime,
                requiredWatchTime: this.requiredWatchTime,
                percentage: percentage,
                unlockCondition: unlockCondition
            });

            if (unlockCondition && !this.isUnlocked) {
                this.triggerUnlock();
            } else if (!unlockCondition) {
                // Log why condition failed (Requirement #7)
                if (this.maxWatchedTime < this.requiredWatchTime) {
                    // console.log(`[VideoTracker] Unlock failed: maxWatchedTime (${this.maxWatchedTime.toFixed(2)}) < requiredWatchTime (${this.requiredWatchTime.toFixed(2)})`);
                }
            }
        }, 1000);

        if (!this.heartbeatInterval) {
            this.heartbeatInterval = setInterval(() => this.heartbeat(), 5000);
        }
    }

    stopTracking() {
        if (this.watchInterval) {
            clearInterval(this.watchInterval);
            this.watchInterval = null;
        }
    }

    triggerUnlock() {
        this.isUnlocked = true;
        console.log("%c UNLOCK TRIGGERED ", "background: #28a745; color: white; font-weight: bold;");
        const nextBtn = document.getElementById(this.nextBtnId);
        if (nextBtn) {
            nextBtn.disabled = false;
        }
        this.onUnlock(this.currentIndex);
    }

    async heartbeat() {
        if (!this.player || this.player.getPlayerState() !== YT.PlayerState.PLAYING) return;

        const percentage = (this.maxWatchedTime / this.totalDuration) * 100;
        try {
            await apiFetch("/progress/update", {
                method: "POST",
                body: JSON.stringify({
                    course_id: this.courseId,
                    video_id: this.currentIndex,
                    last_watched_time: this.maxWatchedTime,
                    duration: this.totalDuration,
                    percentage: percentage
                })
            });
        } catch (e) {
            console.error("[VideoTracker] Heartbeat failed", e);
        }
    }

    async fetchVideoState(index) {
        try {
            return await apiFetch(`/progress/${this.courseId}/${index}`);
        } catch (e) {
            console.error("[VideoTracker] Fetch state failed", e);
            return null;
        }
    }
}
