"""邮件发送工具"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.core.config import settings


async def send_email(
    to_emails: List[str],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """发送邮件
    
    Args:
        to_emails: 收件人邮箱列表
        subject: 邮件主题
        html_content: HTML内容
        text_content: 纯文本内容（可选）
        
    Returns:
        bool: 是否发送成功
    """
    try:
        # 创建邮件对象
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = ", ".join(to_emails)
        
        # 添加纯文本部分
        if text_content:
            text_part = MIMEText(text_content, "plain")
            msg.attach(text_part)
        
        # 添加HTML部分
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)
        
        # 连接SMTP服务器并发送
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False


async def send_verification_email(email: str, token: str) -> bool:
    """发送验证邮件"""
    subject = "验证您的邮箱"
    verify_url = f"{settings.FRONTEND_URL}/verify?token={token}"
    
    html_content = f"""
    <html>
        <body>
            <h2>欢迎注册！</h2>
            <p>请点击下面的链接验证您的邮箱：</p>
            <a href="{verify_url}">验证邮箱</a>
            <p>如果您没有注册账号，请忽略此邮件。</p>
        </body>
    </html>
    """
    
    text_content = f"""
    欢迎注册！
    
    请访问以下链接验证您的邮箱：
    {verify_url}
    
    如果您没有注册账号，请忽略此邮件。
    """
    
    return await send_email([email], subject, html_content, text_content)


async def send_password_reset_email(email: str, token: str) -> bool:
    """发送密码重置邮件"""
    subject = "重置您的密码"
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    html_content = f"""
    <html>
        <body>
            <h2>重置密码</h2>
            <p>请点击下面的链接重置您的密码：</p>
            <a href="{reset_url}">重置密码</a>
            <p>链接将在30分钟后失效。</p>
            <p>如果您没有请求重置密码，请忽略此邮件。</p>
        </body>
    </html>
    """
    
    text_content = f"""
    重置密码
    
    请访问以下链接重置您的密码：
    {reset_url}
    
    链接将在30分钟后失效。
    
    如果您没有请求重置密码，请忽略此邮件。
    """
    
    return await send_email([email], subject, html_content, text_content)

