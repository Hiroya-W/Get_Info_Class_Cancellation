import get_cancel_info
import get_my_info
import create_delete_schedule
from apscheduler.schedulers.blocking import BlockingScheduler


def job():
    # 休講情報を取得
    get_cancel_info.main()
    # 全クラスごとの登録されている休講情報を取得
    get_my_info.main()
    # 予定を追加 & 削除する
    create_delete_schedule.main()


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, "cron", minute=30)
    # scheduler.add_job(job, "interval", minutes=1)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        pass
