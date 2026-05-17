import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
    const [ip, setIp] = useState("");
    const [user, setUser] = useState("");
    const [pass, setPass] = useState("");
    const [ports, setPorts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isMonitoring, setIsMonitoring] = useState(false); // Novo estado para controlar o monitoramento

    // Estados para o popup
    const [popupContent, setPopupContent] = useState("");
    const [showPopup, setShowPopup] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);

    // Função que busca os dados no backend
    const buscarDados = async () => {
        if (!ip || !user || !pass) return;

        try {
            const res = await axios.post("http://192.168.200.11:5000/conectar", {
                ip,
                user,
                pass,
            });
            setPorts(res.data);
        } catch (err) {
            console.error("Erro na atualização automática:", err);
            // Se der erro crítico, podemos parar o monitoramento para evitar loops de erro
            if (err.response?.status === 500) setIsMonitoring(false);
        }
    };

    // useEffect que gerencia o timer de 3 segundos
    useEffect(() => {
        let intervalo;

        if (isMonitoring) {
            // Define o intervalo de 3000ms (3 segundos)
            intervalo = setInterval(() => {
                buscarDados();
            }, 3000);
        }

        // Limpa o intervalo se o componente for fechado ou o monitoramento parado
        return () => clearInterval(intervalo);
    }, [isMonitoring, ip, user, pass]); 

    const handleConectar = async () => {
        setLoading(true);
        await buscarDados(); // Faz a primeira busca imediatamente
        setIsMonitoring(true); // Ativa o monitoramento automático
        setLoading(false);
    };

    const handleParar = () => {
        setIsMonitoring(false);
    };

    const handleAnalisar = async (p) => {
        setAnalyzing(true);
        try {
            const texto = `Porta: ${p.porta || p.interface}, Status: ${p.status}, VLAN: ${p.vlan}, Velocidade: ${p.velocidade}`;
            const res = await axios.post("http://192.168.200.11:5000/analisar", { texto });
            setPopupContent(res.data.resultado);
            setShowPopup(true);
        } catch (err) {
            console.error("Erro ao analisar a porta:", err);
            alert("Falha ao conectar com o serviço de IA.");
        } finally {
            setAnalyzing(false);
        }
    };

    return (
        <div className="container">
            <h1>Network Monitor Pro</h1>

            <div className="form">
                <input 
                    placeholder="IP do Switch" 
                    value={ip}
                    onChange={(e) => setIp(e.target.value)} 
                />
                <input 
                    placeholder="Usuário" 
                    value={user}
                    onChange={(e) => setUser(e.target.value)} 
                />
                <input
                    type="password"
                    placeholder="Senha"
                    value={pass}
                    onChange={(e) => setPass(e.target.value)}
                />
                
                {!isMonitoring ? (
                    <button onClick={handleConectar} disabled={loading}>
                        {loading ? "Conectando..." : "Iniciar Monitoramento"}
                    </button>
                ) : (
                    <button onClick={handleParar} style={{ backgroundColor: "#dc3545" }}>
                        Parar Monitoramento
                    </button>
                )}
            </div>

            {isMonitoring && <p className="status-live">🔴 Live: Atualizando a cada 3s</p>}

            <table>
                <thead>
                    <tr>
                        <th>Porta</th>
                        <th>Status</th>
                        <th>VLAN</th>
                        <th>Velocidade</th>
                        <th>Ação</th>
                    </tr>
                </thead>
                <tbody>
                    {ports.length > 0 ? (
                        ports.map((p, i) => {
                            const isUp = p.status === "CONNECTED" || p.status === "UP";
                            return (
                                <tr key={i}>
                                    <td>{p.porta || p.interface}</td>
                                    <td className={isUp ? "status-up" : "status-down"}>
                                        {p.status}
                                    </td>
                                    <td>{p.vlan}</td>
                                    <td>{p.velocidade}</td>
                                    <td>
                                        <button
                                            className="analyze-btn"
                                            onClick={() => handleAnalisar(p)}
                                            disabled={analyzing}
                                        >
                                            {analyzing ? "..." : "Analisar"}
                                        </button>
                                    </td>
                                </tr>
                            );
                        })
                    ) : (
                        <tr>
                            <td colSpan="5" style={{ textAlign: "center" }}>
                                {loading ? "Buscando dados..." : "Aguardando conexão."}
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>

            {showPopup && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <h3>Parecer da IA (Groq)</h3>
                        <pre>{popupContent}</pre>
                        <button className="modal-close" onClick={() => setShowPopup(false)}>
                            Fechar
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
