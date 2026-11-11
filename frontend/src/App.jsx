import { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";

function App() {
    const [ip, setIp] = useState("");
    const [user, setUser] = useState("");
    const [pass, setPass] = useState("");
    const [ports, setPorts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isMonitoring, setIsMonitoring] = useState(false);

    // Estados para o Chat e Histórico (Carrega do localStorage se houver)
    const [showChat, setShowChat] = useState(false);
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState("");
    const [analyzing, setAnalyzing] = useState(false);
    const [selectedPort, setSelectedPort] = useState(null);
    
    // Estados do Histórico de Sessões salvos no localStorage
    const [sessions, setSessions] = useState(() => {
        const savedSessions = localStorage.getItem("network_chat_sessions");
        return savedSessions ? JSON.parse(savedSessions) : [];
    });
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const [activeTab, setActiveTab] = useState("chat"); // "chat" ou "history"

    const chatEndRef = useRef(null);

    // Salva as sessões no localStorage sempre que o array 'sessions' for atualizado
    useEffect(() => {
        localStorage.setItem("network_chat_sessions", JSON.stringify(sessions));
    }, [sessions]);

    // Auto-scroll para a última mensagem do chat
    useEffect(() => {
        if (activeTab === "chat") {
            chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, activeTab]);

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
            if (err.response?.status === 500) setIsMonitoring(false);
        }
    };

    useEffect(() => {
        let intervalo;
        if (isMonitoring) {
            intervalo = setInterval(() => {
                buscarDados();
            }, 3000);
        }
        return () => clearInterval(intervalo);
    }, [isMonitoring, ip, user, pass]); 

    const handleConectar = async () => {
        setLoading(true);
        await buscarDados();
        setIsMonitoring(true);
        setLoading(false);
    };

    const handleParar = () => {
        setIsMonitoring(false);
        setPorts([]); // Limpa as portas para elas sumirem da tabela
    };

    // Inicia a conversa e cria uma nova sessão no histórico
    const handleAnalisar = async (p) => {
        setSelectedPort(p);
        setShowChat(true);
        setActiveTab("chat");
        setAnalyzing(true);

        const newSessionId = Date.now();
        const portName = p.porta || p.interface;
        const initialPrompt = `Analise esta porta de switch: Porta: ${portName}, Status: ${p.status}, VLAN: ${p.vlan}, Velocidade: ${p.velocidade}`;
        
        const userMsg = { sender: "user", text: `Analisar porta ${portName}` };
        const initialMessages = [userMsg];
        
        setMessages(initialMessages);
        setCurrentSessionId(newSessionId);

        try {
            const res = await axios.post("http://192.168.200.11:5000/analisar", { texto: initialPrompt });
            const aiMsg = { sender: "ai", text: res.data.resultado };
            const finalMessages = [...initialMessages, aiMsg];
            
            setMessages(finalMessages);

            // Adiciona ao histórico de sessões
            setSessions(prev => [
                ...prev, 
                { 
                    id: newSessionId, 
                    title: `Porta ${portName}`, 
                    port: p, 
                    messages: finalMessages, 
                    date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
                }
            ]);
        } catch (err) {
            console.error("Erro ao analisar a porta:", err);
            const errorMsg = { sender: "ai", text: "Erro ao conectar com o serviço de IA." };
            const finalMessages = [...initialMessages, errorMsg];
            setMessages(finalMessages);
        } finally {
            setAnalyzing(false);
        }
    };

    // Atualiza as mensagens da sessão atual no histórico
    const updateCurrentSession = (newMsgs) => {
        setSessions(prev => prev.map(s => s.id === currentSessionId ? { ...s, messages: newMsgs } : s));
    };

    // Envia novas perguntas no chat ativo com todas as portas como contexto
    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim() || analyzing) return;

        const perguntaUsuario = inputMessage;
        setInputMessage("");
        const updatedMessages = [...messages, { sender: "user", text: perguntaUsuario }];
        setMessages(updatedMessages);
        setAnalyzing(true);

        updateCurrentSession(updatedMessages);

        try {
            const listaPortasTexto = ports.map(p => 
                `Porta: ${p.porta || p.interface}, Status: ${p.status}, VLAN: ${p.vlan}, Velocidade: ${p.velocidade}`
            ).join(" | ");

            const contextoGeral = `[Dados de todas as portas do switch: ${listaPortasTexto}]`;
            const textoCompleto = `${contextoGeral}\n\nPergunta do operador: ${perguntaUsuario}`;

            const res = await axios.post("http://192.168.200.11:5000/analisar", { texto: textoCompleto });
            const finalMessagesWithAi = [...updatedMessages, { sender: "ai", text: res.data.resultado }];
            
            setMessages(finalMessagesWithAi);
            updateCurrentSession(finalMessagesWithAi);
        } catch (err) {
            console.error("Erro no chat:", err);
            const errorMessages = [...updatedMessages, { sender: "ai", text: "Erro ao processar a sua pergunta." }];
            setMessages(errorMessages);
            updateCurrentSession(errorMessages);
        } finally {
            setAnalyzing(false);
        }
    };

    // Voltar para um histórico anterior
    const handleSelectSession = (session) => {
        setSelectedPort(session.port);
        setMessages(session.messages);
        setCurrentSessionId(session.id);
        setActiveTab("chat");
    };

    // Apagar/Fechar um histórico específico da lista
    const handleDeleteSession = (sessionId, e) => {
        e.stopPropagation(); 
        setSessions(prev => prev.filter(s => s.id !== sessionId));
        
        if (currentSessionId === sessionId) {
            setCurrentSessionId(null);
            setMessages([]);
            setSelectedPort(null);
        }
    };

    // Limpar todo o histórico e apagar do localStorage
    const handleClearHistory = () => {
        setSessions([]);
        setCurrentSessionId(null);
        localStorage.removeItem("network_chat_sessions");
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
                    placeholder="Utilizador" 
                    value={user}
                    onChange={(e) => setUser(e.target.value)} 
                />
                <input
                    type="password"
                    placeholder="Palavra-passe"
                    value={pass}
                    onChange={(e) => setPass(e.target.value)}
                />
                
                {!isMonitoring ? (
                    <button onClick={handleConectar} disabled={loading}>
                        {loading ? "A conectar..." : "Iniciar Monitoramento"}
                    </button>
                ) : (
                    <button onClick={handleParar} style={{ backgroundColor: "#dc3545" }}>
                        Parar Monitoramento
                    </button>
                )}
            </div>

            {isMonitoring && <p className="status-live">🔴 Live: A atualizar a cada 3s</p>}

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
                                            Analisar
                                        </button>
                                    </td>
                                </tr>
                            );
                        })
                    ) : (
                        <tr>
                            <td colSpan="5" style={{ textAlign: "center" }}>
                                {loading ? "A procurar dados..." : "À espera de conexão."}
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>

            {/* Gaveta Lateral de Chat com Abas (Chat / Histórico) */}
            {showChat && (
                <div className="chat-drawer">
                    <div className="chat-header">
                        <h3>🤖 IA Assistant</h3>
                        <button className="chat-close" onClick={() => setShowChat(false)}>✕</button>
                    </div>

                    {/* Abas de Navegação */}
                    <div className="chat-tabs">
                        <button 
                            className={`chat-tab-btn ${activeTab === "chat" ? "active" : ""}`} 
                            onClick={() => setActiveTab("chat")}
                        >
                            Conversa Atual
                        </button>
                        <button 
                            className={`chat-tab-btn ${activeTab === "history" ? "active" : ""}`} 
                            onClick={() => setActiveTab("history")}
                        >
                            Histórico ({sessions.length})
                        </button>
                    </div>
                    
                    {activeTab === "chat" ? (
                        <>
                            <div className="chat-body">
                                {messages.length === 0 ? (
                                    <p className="chat-empty">Selecione uma porta e clique em "Analisar" para iniciar.</p>
                                ) : (
                                    messages.map((msg, index) => (
                                        <div key={index} className={`chat-message ${msg.sender === "user" ? "user-message" : "ai-message"}`}>
                                            <pre>{msg.text}</pre>
                                        </div>
                                    ))
                                )}
                                {analyzing && <div className="chat-message ai-message"><pre>A escrever...</pre></div>}
                                <div ref={chatEndRef} />
                            </div>

                            <form className="chat-input-form" onSubmit={handleSendMessage}>
                                <input 
                                    type="text" 
                                    placeholder="Pergunte algo sobre a porta..." 
                                    value={inputMessage}
                                    onChange={(e) => setInputMessage(e.target.value)}
                                />
                                <button type="submit" disabled={analyzing || ports.length === 0}>Enviar</button>
                            </form>
                        </>
                    ) : (
                        <div className="history-body">
                            <div className="history-header-actions">
                                <span>Análises Anteriores</span>
                                {sessions.length > 0 && (
                                    <button className="clear-history-btn" onClick={handleClearHistory}>Limpar Tudo</button>
                                )}
                            </div>
                            {sessions.length === 0 ? (
                                <p className="chat-empty">Nenhum histórico guardado.</p>
                            ) : (
                                <div className="history-list">
                                    {sessions.map((session) => (
                                        <div 
                                            key={session.id} 
                                            className={`history-item ${session.id === currentSessionId ? "active" : ""}`}
                                            onClick={() => handleSelectSession(session)}
                                        >
                                            <div className="history-info">
                                                <div className="history-title">🖥️ {session.title}</div>
                                                <div className="history-time">{session.date}</div>
                                            </div>
                                            <button 
                                                className="delete-history-item-btn" 
                                                onClick={(e) => handleDeleteSession(session.id, e)}
                                                title="Fechar este histórico"
                                            >
                                                ✕
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default App;
