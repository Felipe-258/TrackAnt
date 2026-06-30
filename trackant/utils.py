from datetime import date


def time_until_deadline(deadline, is_done=False):
    if not deadline or is_done:
        return None
    days = (deadline - date.today()).days
    if days < 0:
        return 'Vencida'
    if days == 0:
        return 'Hoy'
    if days == 1:
        return 'Mañana'
    if days <= 7:
        return f'{days} días'
    if days <= 30:
        weeks = days // 7
        return f'{weeks} {"semana" if weeks == 1 else "semanas"}'
    if days <= 365:
        months = days // 30
        return f'{months} {"mes" if months == 1 else "meses"}'
    years = days // 365
    return f'{years} {"año" if years == 1 else "años"}'
