import os
import time

if __name__ == "__main__":
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"report_{timestamp}.html")
    exit_code = os.system(f'pytest --html="{report_file}" --self-contained-html')
    print(f"\n测试报告已生成: {report_file}")
    exit(exit_code) 