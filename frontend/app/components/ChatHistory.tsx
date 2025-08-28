import { format } from "date-fns";
import { nb } from "date-fns/locale";

type ChatLog = {
  threadData: {
    threadFrom: {
      message: string;
      date: Date;
    };
    threadTo: {
      message: string;
      date: Date;
    };
  }[];
  leadName: string;
};

function ChatHistory({ threadData, leadName }: ChatLog) {
  return (
    <>
      {threadData.map((m, i) => (
        <div key={i}>
          <div className="chat chat-end">
            <div className="chat-image avatar">
              <div className="w-10 rounded-full">
                <img
                  alt="Tailwind CSS chat bubble component"
                  src="/bakgrunnn.png"
                />
              </div>
            </div>
            <div className="chat-header">
              Ciri
              <time className="chat-header opacity-50">
                {format(m.threadFrom.date, "d. MMM yyyy 'kl.' HH:mm", {
                  locale: nb,
                })}
              </time>
            </div>
            <div className="chat-bubble opacity-90">{m.threadFrom.message}</div>
            <div className="chat-footer opacity-50">Sendt</div>
          </div>
          <div className="chat chat-start">
            <div className="chat-image avatar">
              <div className="w-10 rounded-full">
                <img
                  alt="Tailwind CSS chat bubble component"
                  src="/artavatar.png"
                />
              </div>
            </div>
            <div className="chat-header">
              {leadName}
              <time className="chat-header opacity-50">
                {format(m.threadTo.date, "d. MMM yyyy 'kl.' HH:mm", {
                  locale: nb,
                })}
              </time>
            </div>
            <div className="chat-bubble">{m.threadTo.message}</div>
            {/* <div className="chat-footer opacity-50">Seen</div> */}
          </div>
        </div>
      ))}
    </>
  );
}

export default ChatHistory;
