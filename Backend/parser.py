import re

def parse_show_interface_status(output):
    """
    Analisa a saída do comando 'show interface status' e extrai
    informações como porta, status, vlan e velocidade.
    """
    interfaces = []
    lines = output.splitlines()

    for line in lines:
        if not line.strip() or "Port" in line or "----" in line:
            continue

        parts = line.split()
        # No 'show interface status', o status e a vlan são cruciais
        if len(parts) >= 3:
            port = parts[0]
            status = "UNKNOWN"
            vlan = "N/A"
            velocidade = "Auto"

            # Lista de status possíveis no comando 'show interface status'
            status_keywords = ["connected", "notconnect", "err-disabled", "disabled", "monitoring"]
            
            for part in parts:
                p_lower = part.lower()
                if p_lower in status_keywords:
                    status = part.upper()
                    idx = parts.index(part)

                    # Geralmente a VLAN vem logo após o status
                    if idx + 1 < len(parts):
                        vlan = parts[idx + 1]
                    # A velocidade costuma vir após o duplex (que vem após a vlan)
                    if idx + 3 < len(parts):
                        velocidade = parts[idx + 3]
                    break

            interfaces.append({
                "porta": port,
                "status": status,
                "vlan": vlan,
                "velocidade": velocidade
            })

    return interfaces
